"""
Test database connection.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def test_connection():
    """Test MongoDB connection."""
    print("[INFO] Connecting to MongoDB...")

    try:
        # Use port 27018 to connect to Docker MongoDB (avoid WSL conflict)
        client = AsyncIOMotorClient(
            "mongodb://localhost:27018",
            serverSelectionTimeoutMS=5000
        )

        # Test connection
        await client.admin.command('ping')
        print("[OK] MongoDB connected")

        # Try to query users
        db = client["ocr_saas"]
        users = db.users

        print("[INFO] Querying users collection...")
        user = await users.find_one({"username": "admin"})

        if user:
            print(f"[OK] Found user: {user.get('username')}")
            print(f"     Role: {user.get('role')}")
            print(f"     Auth type: {user.get('auth_type')}")
        else:
            print("[WARN] User not found")

        client.close()
        print("[OK] Test completed successfully")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
