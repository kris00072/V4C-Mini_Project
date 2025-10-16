import os
import sqlite3
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read environment variables
SQLITE_FILE = os.getenv("SQLITE_FILE", "company.db")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "performance_reviews_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "reviews")

def test_sqlite():
    try:
        conn = sqlite3.connect(SQLITE_FILE)
        cur = conn.cursor()
        # Create a simple table to test
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        """)
        conn.commit()
        print("✅ SQLite connection successful and table created.")
    except Exception as e:
        print("❌ SQLite connection failed:", e)
    finally:
        conn.close()

def test_mongo():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        # Test insert
        test_doc = {"test": "connection"}
        result = collection.insert_one(test_doc)
        # Test find
        found = collection.find_one({"_id": result.inserted_id})
        print("✅ MongoDB connection successful!")
        print("   Database:", db.name)
        print("   Collection:", collection.name)
        print("   Test document inserted:", found)
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
    finally:
        client.close()

if __name__ == "__main__":
    print("🔍 Testing database connections...\n")
    test_sqlite()
    test_mongo()
