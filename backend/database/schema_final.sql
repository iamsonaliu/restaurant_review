-- ============================================
-- DINEWISE DATABASE SCHEMA (Oracle 11g Compatible)
-- ============================================

-- ============================================
-- DROP TABLES (if exist)
-- ============================================
BEGIN EXECUTE IMMEDIATE 'DROP TABLE REVIEWS CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE RATINGS CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE RESTAURANT_CATEGORIES CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE CATEGORIES CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE RESTAURANTS CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE USERS CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- ============================================
-- DROP SEQUENCES (if exist)
-- ============================================
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE user_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE restaurant_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE category_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE review_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE rating_seq'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- ============================================
-- CREATE SEQUENCES
-- ============================================
CREATE SEQUENCE user_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE restaurant_seq START WITH 1001 INCREMENT BY 1;
CREATE SEQUENCE category_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE review_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE rating_seq START WITH 1 INCREMENT BY 1;

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE USERS (
    user_id VARCHAR2(36) PRIMARY KEY,
    username VARCHAR2(100) NOT NULL UNIQUE,
    email VARCHAR2(100) NOT NULL UNIQUE,
    password_hash VARCHAR2(255) NOT NULL,
    registration_date DATE DEFAULT SYSDATE NOT NULL,
    role VARCHAR2(20) DEFAULT 'user' CHECK (role IN ('user', 'admin'))
);

-- ============================================
-- RESTAURANTS TABLE
-- ============================================
CREATE TABLE RESTAURANTS (
    restaurant_id VARCHAR2(36) PRIMARY KEY,
    name VARCHAR2(200) NOT NULL,
    address VARCHAR2(255) NOT NULL,
    city VARCHAR2(100) NOT NULL CHECK (city IN ('Dehradun', 'Haridwar', 'Mussoorie', 'Rishikesh')),
    region VARCHAR2(100),
    phone_number VARCHAR2(20),
    website_url VARCHAR2(500),
    avg_rating NUMBER(3,2) DEFAULT 0 CHECK (avg_rating BETWEEN 0 AND 5),
    price_range NUMBER(10,0),
    dining_type VARCHAR2(50),
    timings VARCHAR2(100),
    votes NUMBER(10,0) DEFAULT 0,
    rating_type VARCHAR2(50),
    created_at DATE DEFAULT SYSDATE
);

-- ============================================
-- CATEGORIES TABLE
-- ============================================
CREATE TABLE CATEGORIES (
    category_id VARCHAR2(36) PRIMARY KEY,
    category_name VARCHAR2(50) NOT NULL UNIQUE
);

-- ============================================
-- RESTAURANT_CATEGORIES (Many-to-Many)
-- ============================================
CREATE TABLE RESTAURANT_CATEGORIES (
    restaurant_id VARCHAR2(36),
    category_id VARCHAR2(36),
    PRIMARY KEY (restaurant_id, category_id),
    FOREIGN KEY (restaurant_id) REFERENCES RESTAURANTS(restaurant_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE CASCADE
);

-- ============================================
-- REVIEWS TABLE
-- ============================================
CREATE TABLE REVIEWS (
    review_id VARCHAR2(36) PRIMARY KEY,
    user_id VARCHAR2(36) NOT NULL,
    restaurant_id VARCHAR2(36) NOT NULL,
    review_text CLOB NOT NULL,
    review_date DATE DEFAULT SYSDATE NOT NULL,
    helpful_count NUMBER(10,0) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES RESTAURANTS(restaurant_id) ON DELETE CASCADE
);

-- ============================================
-- RATINGS TABLE
-- ============================================
CREATE TABLE RATINGS (
    rating_id VARCHAR2(36) PRIMARY KEY,
    user_id VARCHAR2(36) NOT NULL,
    restaurant_id VARCHAR2(36) NOT NULL,
    rating_value NUMBER(2,1) NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
    rating_date DATE DEFAULT SYSDATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES RESTAURANTS(restaurant_id) ON DELETE CASCADE,
    UNIQUE (user_id, restaurant_id)
);

-- ============================================
-- INDEXES (no duplicates)
-- ============================================
CREATE INDEX idx_restaurant_city ON RESTAURANTS(city);
CREATE INDEX idx_restaurant_rating ON RESTAURANTS(avg_rating);
CREATE INDEX idx_restaurant_name ON RESTAURANTS(name);

CREATE INDEX idx_review_restaurant ON REVIEWS(restaurant_id);
CREATE INDEX idx_review_user ON REVIEWS(user_id);

CREATE INDEX idx_rating_restaurant ON RATINGS(restaurant_id);
CREATE INDEX idx_rating_user ON RATINGS(user_id);

-- DO NOT ADD: idx_category_name (unique index already created by UNIQUE constraint)

-- ============================================
-- COMPOUND TRIGGER (fixes mutating table error)
-- ============================================
CREATE OR REPLACE TRIGGER trg_update_avg_rating
FOR INSERT OR UPDATE OR DELETE ON ratings
COMPOUND TRIGGER

    TYPE t_rest_list IS TABLE OF ratings.restaurant_id%TYPE;
    g_rest_ids t_rest_list := t_rest_list();

AFTER EACH ROW IS
BEGIN
    IF INSERTING THEN
        g_rest_ids.EXTEND;
        g_rest_ids(g_rest_ids.LAST) := :NEW.restaurant_id;

    ELSIF UPDATING THEN
        g_rest_ids.EXTEND;
        g_rest_ids(g_rest_ids.LAST) := :NEW.restaurant_id;

    ELSIF DELETING THEN
        g_rest_ids.EXTEND;
        g_rest_ids(g_rest_ids.LAST) := :OLD.restaurant_id;
    END IF;
END AFTER EACH ROW;

AFTER STATEMENT IS
BEGIN
    DECLARE v_rest_id VARCHAR2(36);
    BEGIN
        FOR i IN 1 .. g_rest_ids.COUNT LOOP
            v_rest_id := g_rest_ids(i);

            UPDATE restaurants r
            SET (avg_rating, votes) =
                ( SELECT NVL(ROUND(AVG(rating_value), 1), 0),
                         COUNT(*)
                  FROM ratings
                  WHERE restaurant_id = v_rest_id )
            WHERE r.restaurant_id = v_rest_id;
        END LOOP;
    END;
END AFTER STATEMENT;

END trg_update_avg_rating;
/

-- ============================================
-- STORED PROCEDURES (Oracle 11g Compatible)
-- ============================================

-- Top restaurants (11g-safe: no FETCH FIRST)
CREATE OR REPLACE PROCEDURE sp_get_top_restaurants(
    p_city IN VARCHAR2,
    p_limit IN NUMBER,
    p_cursor OUT SYS_REFCURSOR
) AS
BEGIN
    OPEN p_cursor FOR
        SELECT *
        FROM (
            SELECT 
                r.restaurant_id,
                r.name,
                r.address,
                r.region,
                r.avg_rating,
                r.votes,
                r.price_range,
                r.dining_type
            FROM RESTAURANTS r
            WHERE r.city = p_city
            ORDER BY r.avg_rating DESC, r.votes DESC
        )
        WHERE ROWNUM <= p_limit;
END;
/
 
-- User statistics
CREATE OR REPLACE PROCEDURE sp_get_user_stats(
    p_user_id IN VARCHAR2,
    p_review_count OUT NUMBER,
    p_rating_count OUT NUMBER,
    p_avg_rating OUT NUMBER
) AS
BEGIN
    SELECT COUNT(*) INTO p_review_count
    FROM REVIEWS WHERE user_id = p_user_id;
    
    SELECT COUNT(*), NVL(AVG(rating_value), 0)
    INTO p_rating_count, p_avg_rating
    FROM RATINGS WHERE user_id = p_user_id;
END;
/

-- Restaurant details with categories
CREATE OR REPLACE PROCEDURE sp_get_restaurant_details(
    p_restaurant_id IN VARCHAR2,
    p_cursor OUT SYS_REFCURSOR
) AS
BEGIN
    OPEN p_cursor FOR
        SELECT 
            r.*,
            LISTAGG(c.category_name, ', ') 
                WITHIN GROUP (ORDER BY c.category_name) AS cuisines
        FROM RESTAURANTS r
        LEFT JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
        LEFT JOIN CATEGORIES c ON rc.category_id = c.category_id
        WHERE r.restaurant_id = p_restaurant_id
        GROUP BY r.restaurant_id, r.name, r.address, r.city, r.region,
                 r.phone_number, r.website_url, r.avg_rating, r.price_range,
                 r.dining_type, r.timings, r.votes, r.rating_type, r.created_at;
END;
/

-- ============================================
-- VIEWS
-- ============================================

CREATE OR REPLACE VIEW vw_restaurant_summary AS
SELECT 
    r.restaurant_id,
    r.name,
    r.city,
    r.region,
    r.avg_rating,
    r.votes,
    r.price_range,
    r.dining_type,
    r.rating_type,
    LISTAGG(c.category_name, ', ') 
        WITHIN GROUP (ORDER BY c.category_name) AS cuisines,
    COUNT(DISTINCT rev.review_id) AS review_count
FROM RESTAURANTS r
LEFT JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
LEFT JOIN CATEGORIES c ON rc.category_id = c.category_id
LEFT JOIN REVIEWS rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.city, r.region, r.avg_rating, 
         r.votes, r.price_range, r.dining_type, r.rating_type;

CREATE OR REPLACE VIEW vw_user_activity AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    u.registration_date,
    COUNT(DISTINCT rat.rating_id) AS ratings_given,
    COUNT(DISTINCT rev.review_id) AS reviews_written,
    NVL(AVG(rat.rating_value), 0) AS avg_rating_given
FROM USERS u
LEFT JOIN RATINGS rat ON u.user_id = rat.user_id
LEFT JOIN REVIEWS rev ON u.user_id = rev.user_id
GROUP BY u.user_id, u.username, u.email, u.registration_date;

CREATE OR REPLACE VIEW vw_city_statistics AS
SELECT 
    city,
    COUNT(*) AS total_restaurants,
    ROUND(AVG(avg_rating), 2) AS avg_city_rating,
    SUM(votes) AS total_votes,
    MIN(price_range) AS min_price,
    MAX(price_range) AS max_price
FROM RESTAURANTS
GROUP BY city;

COMMIT;
