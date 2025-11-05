# import_hybrid_data.py

import csv
import re
from pathlib import Path
import random
from datetime import datetime, timedelta

import oracledb

# ================================
# ORACLE CLIENT (THICK MODE) - 11g
# ================================
INSTANT_CLIENT_DIR = r"C:\Users\sonal\OneDrive\Desktop\PBL_5TH SEM\instantclient_19_28"
oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)

# ================================
# DATABASE CONNECTION
# ================================
DB_CONFIG = {
    "user": "system",
    "password": "oracle",
    "dsn": "localhost:1522/xe",   # your listener shows 1522 and service 'xe'
}

# ================================
# FILE PATH (no \D warnings)
# ================================
CSV_PATH = Path(r"C:\Users\sonal\OneDrive\Desktop\PBL_5TH SEM\DBMS\restaurant_reviews\zomato_restaurants.csv")

# ================================
# HELPERS
# ================================
def generate_id(prefix, num):
    """Generate consistent IDs like R0001"""
    return f"{prefix}{str(num).zfill(4)}"

def generate_phone():
    """Generate Indian phone numbers"""
    prefixes = ['9634', '8077', '7088', '9897', '8279', '9568', '7895']
    return f"+91-{random.choice(prefixes)}{random.randint(100000, 999999)}"

def clean_price(price_str):
    """Extract numeric price (₹1,200 -> 1200). Fallback 500."""
    try:
        if price_str is None:
            return 500
        cleaned = str(price_str).replace('₹', '').replace(',', '').strip()
        return int(cleaned) if cleaned else 500
    except Exception:
        return 500

def clean_int(value, default=0):
    """Return int from strings like '1,234', 'NEW', '--'."""
    if value is None:
        return default
    s = str(value).strip()
    if s.upper() in {"NEW", "N/A", "NA", "-", "--", ""}:
        return default
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else default

def clean_float(value, default=3.5):
    """Return float, map 'NEW'/invalid to default."""
    if value is None:
        return default
    s = str(value).strip()
    if s.upper() in {"NEW", "N/A", "NA", "-", "--", ""}:
        return default
    try:
        return float(s.replace(",", ""))
    except Exception:
        return default

def parse_cuisines(cuisine_str):
    """Split cuisines safely."""
    if not cuisine_str:
        return ['Indian']
    return [c.strip() for c in str(cuisine_str).split(',') if c.strip()]

def pick(row, *keys, default=""):
    """Pick first existing key from a DictReader row."""
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return default

# ================================
# USERS
# ================================
def insert_users(connection):
    cursor = connection.cursor()
    print("\n👥 Inserting users...")

    users = [
        ('U001', 'john_foodie', 'john@email.com', 'hash123abc', '2024-01-15'),
        ('U002', 'sarah_eats', 'sarah@email.com', 'hash456def', '2024-02-20'),
        ('U003', 'mike_reviews', 'mike@email.com', 'hash789ghi', '2024-03-10'),
        ('U004', 'emma_diner', 'emma@email.com', 'hashabc123', '2024-04-05'),
        ('U005', 'alex_tasty', 'alex@email.com', 'hashdef456', '2024-05-12'),
        ('U006', 'lisa_gourmet', 'lisa@email.com', 'hashghi789', '2024-01-22'),
        ('U007', 'david_chef', 'david@email.com', 'hashjkl012', '2024-02-14'),
        ('U008', 'maria_taste', 'maria@email.com', 'hashmno345', '2024-03-18'),
        ('U009', 'tom_critic', 'tom@email.com', 'hashpqr678', '2024-04-20'),
        ('U010', 'rachel_food', 'rachel@email.com', 'hashstu901', '2024-05-25'),
        ('U011', 'kevin_eat', 'kevin@email.com', 'hashvwx234', '2024-01-08'),
        ('U012', 'nina_dine', 'nina@email.com', 'hashyza567', '2024-02-28'),
        ('U013', 'paul_hungry', 'paul@email.com', 'hashbcd890', '2024-03-30'),
        ('U014', 'olivia_foodlover', 'olivia@email.com', 'hashefg123', '2024-04-15'),
        ('U015', 'chris_plate', 'chris@email.com', 'hashhij456', '2024-05-08'),
        ('U016', 'jennifer_bite', 'jennifer@email.com', 'hashklm789', '2024-01-30'),
        ('U017', 'ryan_meals', 'ryan@email.com', 'hashnop012', '2024-03-05'),
        ('U018', 'amy_flavor', 'amy@email.com', 'hashqrs345', '2024-04-25'),
        ('U019', 'daniel_cuisine', 'daniel@email.com', 'hashtuv678', '2024-05-19'),
        ('U020', 'sophia_delicious', 'sophia@email.com', 'hashwxy901', '2024-06-02'),
    ]

    for user in users:
        try:
            cursor.execute("""
                INSERT INTO USERS (user_id, username, email, password_hash, registration_date)
                VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'))
            """, user)
        except oracledb.IntegrityError:
            # already exists — ignore
            pass

    # Add admin
    try:
        cursor.execute("""
            INSERT INTO USERS (user_id, username, email, password_hash, role)
            VALUES ('U999', 'admin', 'admin@dinewise.in', 'admin_hash', 'admin')
        """)
    except oracledb.IntegrityError:
        pass

    connection.commit()
    print(f"✅ Users ensured (mock + admin).")
    return [u[0] for u in users]


def get_existing_user_ids(connection):
    cur = connection.cursor()
    try:
        cur.execute("SELECT user_id FROM USERS")
        return [r[0] for r in cur.fetchall()]
    except Exception:
        return []

# ================================
# RESTAURANTS & CATEGORIES
# ================================
def import_zomato_restaurants(connection, csv_file):
    cursor = connection.cursor()
    print(f"\n🏪 Importing restaurants from {csv_file}...")

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"📊 Found {len(rows)} restaurants")

    all_categories = set()
    restaurant_data = []

    for idx, row in enumerate(rows, start=1):
        restaurant_id = generate_id('R', idx)

        name        = (pick(row, 'NAME') or '').strip()
        city        = (pick(row, 'city', 'CITY') or '').strip()
        region      = (pick(row, 'REGION') or '').strip()
        price       = clean_price(pick(row, 'PRICE', 'COST', 'PRICE_RANGE') or '500')
        rating      = clean_float(pick(row, 'RATING'), default=3.5)
        votes       = clean_int(pick(row, 'VOTES', 'REVIEWS', 'VOTE_COUNT'), default=0)
        url_val     = pick(row, 'URL') or ''
        dining_type = (pick(row, 'CUSINE TYPE', 'CUISINE TYPE', 'DINING_TYPE', 'DINING TYPE') or 'Casual Dining').strip()
        timings     = (pick(row, 'TIMING') or '10am to 10pm').strip()
        rating_type = (pick(row, 'RATING_TYPE') or 'Good').strip()
        cuisines    = parse_cuisines(pick(row, 'CUSINE_CATEGORY', 'CUISINE_CATEGORY', 'CUISINES', 'CUISINE') or 'Indian')

        phone = generate_phone()

        restaurant_data.append({
            'id': restaurant_id,
            'name': name,
            'address': region,
            'city': city,
            'region': region,
            'phone': phone,
            'url': url_val[:500],
            'rating': rating,
            'price': price,
            'dining_type': dining_type,
            'timings': timings,
            'votes': votes,
            'rating_type': rating_type,
            'cuisines': cuisines
        })

        all_categories.update(cuisines)

    # Insert categories
    print(f"\n📦 Inserting {len(all_categories)} categories...")
    category_map = {}
    for idx, category in enumerate(sorted(all_categories), start=1):
        cat_id = generate_id('C', idx)
        try:
            cursor.execute("""
                INSERT INTO CATEGORIES (category_id, category_name)
                VALUES (:1, :2)
            """, (cat_id, category))
            category_map[category] = cat_id
        except oracledb.IntegrityError:
            cursor.execute("SELECT category_id FROM CATEGORIES WHERE category_name = :1", (category,))
            row = cursor.fetchone()
            if row:
                category_map[category] = row[0]

    connection.commit()

    # Insert restaurants + relationships
    print(f"\n🏪 Inserting {len(restaurant_data)} restaurants...")
    for idx, rest in enumerate(restaurant_data, start=1):
        try:
            cursor.execute("""
                INSERT INTO RESTAURANTS (
                    restaurant_id, name, address, city, region, phone_number,
                    website_url, avg_rating, price_range, dining_type, 
                    timings, votes, rating_type
                ) VALUES (
                    :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13
                )
            """, (
                rest['id'], rest['name'], rest['address'], rest['city'],
                rest['region'], rest['phone'], rest['url'], rest['rating'],
                rest['price'], rest['dining_type'], rest['timings'],
                rest['votes'], rest['rating_type']
            ))

            for cuisine in rest['cuisines']:
                cat_id = category_map.get(cuisine)
                if cat_id:
                    cursor.execute("""
                        INSERT INTO RESTAURANT_CATEGORIES (restaurant_id, category_id)
                        VALUES (:1, :2)
                    """, (rest['id'], cat_id))

            if idx % 100 == 0:
                print(f"   Progress: {idx}/{len(restaurant_data)} restaurants")
                connection.commit()

        except oracledb.IntegrityError:
            # restaurant already exists or FK issue; skip
            continue
        except Exception as e:
            print(f"   ⚠️  Error inserting {rest['name']}: {e}")
            continue

    connection.commit()
    print(f"✅ Successfully imported {len(restaurant_data)} restaurants!")

    return restaurant_data, category_map


# ================================
# REVIEWS & RATINGS
# ================================
def generate_reviews_ratings(connection, users, restaurants):
    if not users:
        print("⚠️ No users available; skipping reviews/ratings.")
        return

    cursor = connection.cursor()
    print("\n⭐ Generating reviews and ratings...")

    review_templates = {
        5: [
            "Absolutely amazing! The {cuisine} was outstanding. Best {dining_type} in {city}!",
            "Perfect experience! Every dish was delicious. Highly recommend!",
            "Exceptional food and service. Authentic and delicious!",
        ],
        4: [
            "Great place! The {cuisine} was really good. Will visit again.",
            "Very good food quality. Definitely worth visiting in {city}.",
            "Enjoyed the {dining_type} experience. Tasty and decent service.",
        ],
        3: [
            "Decent {cuisine}. Nothing extraordinary but okay for the price.",
            "Average experience. The food was okay but nothing special.",
            "Standard {dining_type}. Service could be better.",
        ],
        2: [
            "Not impressed. The {cuisine} lacked flavor.",
            "Below expectations. Food was mediocre.",
            "Disappointed with the experience. Won't recommend.",
        ]
    }

    rating_count = 0
    review_count = 0

    sampled_restaurants = random.sample(restaurants, min(400, len(restaurants)))

    for rest in sampled_restaurants:
        num_ratings = random.randint(2, 10)
        selected_users = random.sample(users, min(num_ratings, len(users)))

        for user_id in selected_users:
            rating = random.choices(
                [5, 4.5, 4, 3.5, 3, 2.5, 2],
                weights=[20, 25, 30, 15, 7, 2, 1]
            )[0]

            rating_id = generate_id('RAT', rating_count + 1)
            days_ago = random.randint(1, 120)
            rating_date = datetime.now() - timedelta(days=days_ago)

            try:
                cursor.execute("""
                    INSERT INTO RATINGS (rating_id, user_id, restaurant_id, rating_value, rating_date)
                    VALUES (:1, :2, :3, :4, :5)
                """, (rating_id, user_id, rest['id'], rating, rating_date))
                rating_count += 1

                if random.random() < 0.5:
                    review_id = generate_id('REV', review_count + 1)
                    rating_bucket = int(rating) if rating >= 2 else 2
                    template = random.choice(review_templates.get(rating_bucket, review_templates[3]))

                    review_text = template.format(
                        name=rest['name'],
                        city=rest['city'],
                        cuisine=random.choice(rest['cuisines']),
                        dining_type=rest['dining_type']
                    )

                    cursor.execute("""
                        INSERT INTO REVIEWS (review_id, user_id, restaurant_id, review_text, review_date)
                        VALUES (:1, :2, :3, :4, :5)
                    """, (review_id, user_id, rest['id'], review_text, rating_date))
                    review_count += 1

                if rating_count % 100 == 0:
                    connection.commit()
                    print(f"   Progress: {rating_count} ratings, {review_count} reviews")

            except oracledb.IntegrityError:
                continue

    connection.commit()
    print(f"✅ Generated {rating_count} ratings and {review_count} reviews!")

# ================================
# MAIN
# ================================
def main():
    print("=" * 60)
    print("   DINEWISE DATABASE - HYBRID DATA IMPORT")
    print("=" * 60)

    try:
        connection = oracledb.connect(**DB_CONFIG)
        print("\n✅ Connected to Oracle!")
        cursor = connection.cursor()

        # Ensure users exist
        users = get_existing_user_ids(connection)
        if not users:
            users = insert_users(connection)

        # Step 2: Import restaurants
        restaurants, categories = import_zomato_restaurants(connection, str(CSV_PATH))

        # ================================
        # 🚫 Disable trigger before bulk insert
        # ================================
        print("\n⏸️ Disabling trigger TRG_UPDATE_AVG_RATING temporarily...")
        cursor.execute("ALTER TRIGGER SYSTEM.TRG_UPDATE_AVG_RATING DISABLE")

        # Step 3: Generate reviews & ratings
        generate_reviews_ratings(connection, users, restaurants)

        # ================================
        # 📊 Recalculate avg ratings in one go
        # ================================
        print("\n🔄 Recalculating restaurant avg ratings...")
        cursor.execute("""
            MERGE INTO SYSTEM.RESTAURANTS r
            USING (
                SELECT restaurant_id, ROUND(AVG(rating_value), 1) avg_rating
                FROM SYSTEM.RATINGS
                GROUP BY restaurant_id
            ) x
            ON (r.restaurant_id = x.restaurant_id)
            WHEN MATCHED THEN UPDATE SET r.avg_rating = x.avg_rating
        """)
        connection.commit()
        print("✅ Average ratings recalculated!")

        # ================================
        # ▶️ Re-enable trigger
        # ================================
        print("\n▶️ Re-enabling trigger TRG_UPDATE_AVG_RATING...")
        cursor.execute("ALTER TRIGGER SYSTEM.TRG_UPDATE_AVG_RATING ENABLE")
        connection.commit()

        # Print summary
        tables = [
            'USERS', 'RESTAURANTS', 'CATEGORIES',
            'RESTAURANT_CATEGORIES', 'RATINGS', 'REVIEWS'
        ]

        print("\n" + "=" * 60)
        print("   DATABASE SUMMARY")
        print("=" * 60)

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:25} : {count:6} records")

        print("=" * 60)
        connection.close()
        print("\n✅ Import completed successfully!\n")

    except oracledb.Error as error:
        print(f"\n❌ Oracle Error: {error}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
# ================================
# MAIN CALL (DO NOT REMOVE)
# ================================
if __name__ == "__main__":
    main()

