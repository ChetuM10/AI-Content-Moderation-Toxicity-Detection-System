from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'senti_clean')

print("=" * 60)
print("🔍 TESTING MONGODB CONNECTION")
print("=" * 60)
print(f"URI: {MONGO_URI}")
print(f"Database: {MONGO_DB_NAME}")

try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    # Test insert
    print("\n✅ Connected to MongoDB!")
    print("\n📝 Testing insert...")
    
    test_user = {
        "email": "test@test.com",
        "password_hash": "test123",
        "created_at": "2025-10-19"
    }
    
    result = db.users.insert_one(test_user)
    print(f"✅ Inserted test user with ID: {result.inserted_id}")
    
    # Verify insert
    user = db.users.find_one({"email": "test@test.com"})
    if user:
        print(f"✅ Found user: {user['email']}")
        
        # Clean up
        db.users.delete_one({"email": "test@test.com"})
        print("✅ Cleaned up test user")
    
    print("\n" + "=" * 60)
    print("✅ MONGODB IS WORKING CORRECTLY!")
    print("=" * 60)
    
except Exception as e:
    print("\n" + "=" * 60)
    print(f"❌ ERROR: {e}")
    print("=" * 60)
