from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['senti_clean']

@app.route('/test-register', methods=['POST'])
def test_register():
    """Test endpoint to verify registration works"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔍 Received registration request:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
        # Insert directly into MongoDB
        result = db.users.insert_one({
            'email': email,
            'password_hash': password,  # NOT hashed for testing
            'test': True
        })
        
        print(f"✅ Inserted user with ID: {result.inserted_id}")
        
        return jsonify({
            'success': True,
            'message': 'User created!',
            'id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-list-users', methods=['GET'])
def list_users():
    """List all users in database"""
    try:
        users = list(db.users.find())
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': users
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 DEBUG SERVER STARTING")
    print("=" * 60)
    print("Test Registration: POST http://localhost:5001/test-register")
    print("List Users: GET http://localhost:5001/test-list-users")
    print("=" * 60)
    app.run(debug=True, port=5001)
