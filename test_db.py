import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

database_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")

if not database_url:
    print("❌ Error: Neither DATABASE_URL nor SUPABASE_URL found in .env file")
else:
    print(f"🔍 Attempting to connect to database...")
    # Hide password in logs if possible, but for debugging we might need to see the structure
    # Let's print the parts of the URL without the password
    try:
        from urllib.parse import urlparse
        result = urlparse(database_url)
        print(f"Scheme: {result.scheme}")
        print(f"Hostname: {result.hostname}")
        print(f"Port: {result.port}")
        print(f"Database: {result.path}")
        print(f"Username: {result.username}")
    except Exception as e:
        print(f"Parsing error: {e}")

    try:
        conn = psycopg2.connect(database_url)
        print("✅ Success! Connection established.")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"Database version: {db_version}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
