# auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

key=os.getenv('SECRET_KEY')
# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Function to generate JWT token
def create_jwt_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, key, algorithm='HS256')

# Function to decode JWT token
def decode_jwt_token(token):
    try:
        return jwt.decode(token, key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")