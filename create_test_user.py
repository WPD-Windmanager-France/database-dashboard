"""Script to create test user in SQLite database"""

from database import get_sqlite_engine
from sqlalchemy import text

def create_test_user():
    """Create test user for local development"""
    engine = get_sqlite_engine()

    with engine.connect() as conn:
        # Create profiles table if it doesn't exist
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(create_table_query)

        # Check if test user already exists
        check_query = text("SELECT email FROM profiles WHERE email = :email")
        result = conn.execute(check_query, {"email": "test@wpd.fr"})
        existing = result.fetchone()

        if existing:
            print("✅ Test user test@wpd.fr already exists")
        else:
            # Insert test user
            insert_query = text("""
                INSERT INTO profiles (id, email, password, role)
                VALUES (:id, :email, :password, :role)
            """)
            conn.execute(insert_query, {
                "id": "test-user-id",
                "email": "test@wpd.fr",
                "password": "password123",
                "role": "admin"
            })
            print("✅ Test user created successfully!")

        # Commit the transaction
        conn.commit()

        # Verify the user was created
        verify_query = text("SELECT id, email, role FROM profiles WHERE email = :email")
        result = conn.execute(verify_query, {"email": "test@wpd.fr"})
        user = result.fetchone()

        if user:
            print(f"\n📋 User verified:")
            print(f"   ID: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Role: {user[2]}")
            print(f"\n🔑 Test credentials:")
            print(f"   Email: test@wpd.fr")
            print(f"   Password: password123")
        else:
            print("❌ Error: user was not created")

if __name__ == "__main__":
    print("Creating test user for SQLite...\n")
    create_test_user()
