-- ============================================
-- DINEWISE DATABASE SCHEMA - ORACLE 11G
-- Final Version with Zomato Integration
-- ============================================

-- Drop existing tables (clean slate)
DROP TABLE REVIEWS CASCADE CONSTRAINTS;
DROP TABLE RATINGS CASCADE CONSTRAINTS;
DROP TABLE RESTAURANT_CATEGORIES CASCADE CONSTRAINTS;
DROP TABLE CATEGORIES CASCADE CONSTRAINTS;
DROP TABLE RESTAURANTS CASCADE CONSTRAINTS;
DROP TABLE USERS CASCADE CONSTRAINTS;

-- Drop sequences
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE user_seq';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE restaurant_seq';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE category_seq';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE review_seq';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP SEQUENCE rating_seq';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- Create sequences
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
-- RESTAURANTS TABLE (Updated for Zomato)
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
    rating_type VARCHAR2(50),  -- Very Good, Good, etc.
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
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_restaurant_city ON RESTAURANTS(city);
CREATE INDEX idx_restaurant_rating ON RESTAURANTS(avg_rating DESC);
CREATE INDEX idx_restaurant_name ON RESTAURANTS(name);
CREATE INDEX idx_review_restaurant ON REVIEWS(restaurant_id);
CREATE INDEX idx_review_user ON REVIEWS(user_id);
CREATE INDEX idx_rating_restaurant ON RATINGS(restaurant_id);
CREATE INDEX idx_rating_user ON RATINGS(user_id);
CREATE INDEX idx_category_name ON CATEGORIES(category_name);

-- ============================================
-- TRIGGER: Auto-update avg_rating on RATINGS change
-- ============================================
CREATE OR REPLACE TRIGGER trg_update_avg_rating
AFTER INSERT OR UPDATE OR DELETE ON RATINGS
FOR EACH ROW
DECLARE
    v_restaurant_id VARCHAR2(36);
    v_avg_rating NUMBER(3,2);
    v_vote_count NUMBER(10,0);
BEGIN
    -- Determine restaurant_id
    IF INSERTING OR UPDATING THEN
        v_restaurant_id := :NEW.restaurant_id;
    ELSIF DELETING THEN
        v_restaurant_id := :OLD.restaurant_id;
    END IF;
    
    -- Calculate new average
    SELECT NVL(ROUND(AVG(rating_value), 1), 0), COUNT(*)
    INTO v_avg_rating, v_vote_count
    FROM RATINGS
    WHERE restaurant_id = v_restaurant_id;
    
    -- Update restaurant
    UPDATE RESTAURANTS
    SET avg_rating = v_avg_rating,
        votes = v_vote_count
    WHERE restaurant_id = v_restaurant_id;
END;
/

-- ============================================
-- STORED PROCEDURES
-- ============================================

-- Procedure: Get top restaurants by city
CREATE OR REPLACE PROCEDURE sp_get_top_restaurants(
    p_city IN VARCHAR2,
    p_limit IN NUMBER,
    p_cursor OUT SYS_REFCURSOR
) AS
BEGIN
    OPEN p_cursor FOR
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
        FETCH FIRST p_limit ROWS ONLY;
END;
/

-- Procedure: Get user statistics
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

-- Procedure: Get restaurant details with categories
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
-- VIEWS FOR ANALYTICS
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