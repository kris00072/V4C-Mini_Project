# db_connections.py
"""
Database Connections Module
---------------------------
Provides connectivity for both SQLite (structured data) and MongoDB (performance reviews)
for the Employee Performance Tracking System.

Responsibilities:
- Connect to SQLite and initialize tables and indexes
- Connect to MongoDB Atlas using environment variables from a local .env file
- Provide helper functions for safe database access
"""

import os
import sqlite3
from sqlite3 import Error as SQLiteError
from pymongo import MongoClient, errors as MongoErrors
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
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except SQLiteError as e:
        print(f"[ERROR] Could not connect to SQLite DB at {db_file}: {e}")
        raise


def init_sqlite_db(conn):
    """
    Initializes SQLite database with required tables and indexes if they do not exist.
    This is safe to call multiple times.
    """
    try:
        cur = conn.cursor()
        cur.executescript("""
        -- Employees table
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            hire_date TEXT NOT NULL,
            department TEXT
        );

        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL UNIQUE,
            start_date TEXT NOT NULL,
            end_date TEXT,
            status TEXT NOT NULL DEFAULT 'Planning'
        );

        -- EmployeeProjects junction table
        CREATE TABLE IF NOT EXISTS employee_projects (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            assigned_date TEXT NOT NULL DEFAULT (date('now')),
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
            FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            UNIQUE(employee_id, project_id)
        );

        -- Indexes for faster lookups
        CREATE INDEX IF NOT EXISTS idx_employee_projects_emp ON employee_projects(employee_id);
        CREATE INDEX IF NOT EXISTS idx_employee_projects_proj ON employee_projects(project_id);
        """)
        conn.commit()
        
    except SQLiteError as e:
        print(f"[ERROR] Failed to initialize SQLite DB: {e}")
        raise



# MongoDB Connection Helper

def get_mongo_collection(uri=None, db_name=None, collection_name=None):
    """
    Connects to MongoDB and returns the specified collection.
    All parameters fallback to environment variables from the .env file.
    Raises exception if connection fails.
    """
    uri = uri or MONGO_URI
    db_name = db_name or MONGO_DB_NAME
    collection_name = collection_name or MONGO_COLLECTION_NAME

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 5s timeout
        client.server_info()  # trigger exception if cannot connect
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except MongoErrors.ServerSelectionTimeoutError as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
        raise
    except MongoErrors.PyMongoError as e:
        print(f"[ERROR] MongoDB error: {e}")
        raise



# Optional Context Manager

from contextlib import contextmanager

@contextmanager
def sqlite_cursor(db_file=SQLITE_FILE):
    """
    Context manager for SQLite cursor.
    Automatically commits and closes connection.
    """
    conn = get_sqlite_connection(db_file)
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except SQLiteError as e:
        conn.rollback()
        print(f"[ERROR] SQLite operation failed: {e}")
        raise
    finally:
        conn.close()



##for testing, willremove in production

if __name__ == "__main__":
    # SQLite test
    conn = get_sqlite_connection()
    init_sqlite_db(conn)
    print("[INFO] SQLite tables ready.")

    # MongoDB test
    try:
        reviews_col = get_mongo_collection()
        print("[INFO] MongoDB collection ready:", reviews_col.name)
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
    finally:
        client.close()

if __name__ == "__main__":
    print("🔍 Testing database connections...\n")
    test_sqlite()
    test_mongo()
