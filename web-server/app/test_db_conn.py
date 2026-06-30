import sys
from database import SessionLocal
from models import User

def test_connection():
    print("Connecting to Neon PostgreSQL DB...")

    try:
        # Initialize database
        db = SessionLocal()

        # Run simple SELECT query to check connection is working
        user_count = db.query(User).count()

        print("\n*******************")
        print(f"🥳 SUCCESS: Connection established!!!\nCurrent user count in db is: {user_count}")
        print("\n*******************")

        db.close()
        sys.exit(0)

    except Exception as error:
        print("\n-----------------")
        print(f"❌ Connection failed. See details: {str(error)}")
        print("\n-----------------")

        sys.exit(1)

if __name__ == "__main__":
    test_connection()