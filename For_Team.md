1. Create a Python virtual environment
   Make sure it's inside employee_performance_tracker folder
   It's not necessary to create it there but it will keep us all
   on the same directory syntax

Windows:

run :
python -m venv venv

then run :
(if u face any error u might be on powershell - switch powershell terminal to command prompt)

.\venv\Scripts\activate

The (venv) in the terminal means it’s active.

2. Install dependencies

pip install -r requirements.txt

This will install pymongo, dnspython, python-dotenv.

3. Set up .env file

create a .env file inside employee_performance_tracker folder

put this in that file

''' Syntax

MONGO_URI="your_mongodb_atlas_connection_string_here"
SQLITE_FILE="company.db"
MONGO_DB_NAME="performance_reviews_db"
MONGO_COLLECTION_NAME="reviews"

''' Syntax (i have shared values over whatsapp)

4. Test database connections

Run:

python database_connections_test.py

You should see something like:

SQLite connection successful and table created.
MongoDB connection successful!
Database: performance_reviews_db
Collection: reviews
Test document inserted: {...}

If errors happen, check .env and internet connection.

5. Ready for development

Once connections work, you can start coding and adding modules.

6. Notes

Keep .env private. 
SQLite DB is local, no need to push.
Use the virtual environment for all Python commands.
And also please remember to take pull before pushing

7. let's discuss er diagram - data models

-- chalo kaam shuru krdo
