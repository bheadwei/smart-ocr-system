"""
Initialize test user in MongoDB.
Run: python scripts/init_test_user.py
"""
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_user():
    """Create a test admin user."""
    # Connect to MongoDB (synchronous)
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)

    # Test connection
    try:
        client.admin.command('ping')
        print("[OK] MongoDB connected")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")
        return

    db = client["ocr_saas"]
    users_collection = db["users"]

    # Check if test user already exists
    existing = users_collection.find_one({"username": "admin"})
    if existing:
        print("[OK] Test user already exists:")
        print(f"   Username: admin")
        print(f"   Role: {existing.get('role', 'unknown')}")
        client.close()
        return

    # Create test admin user
    test_user = {
        "username": "admin",
        "password_hash": pwd_context.hash("admin123"),
        "display_name": "Admin",
        "email": "admin@example.com",
        "auth_type": "local",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
    }

    result = users_collection.insert_one(test_user)

    print("[OK] Test user created successfully!")
    print("=" * 40)
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Role: admin")
    print(f"   ID: {result.inserted_id}")
    print("=" * 40)

    # Close connection
    client.close()


if __name__ == "__main__":
    create_test_user()
