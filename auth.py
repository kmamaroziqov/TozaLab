# auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import os 
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
load_dotenv()

key=os.getenv('SECRET_KEY')
# Function to hash passwords

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify passwords

def verify_password(plain_password, hashed_password):
    # Ensure plain_password is encoded to bytes, but hashed_password remains as-is
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Function to generate JWT token
def create_jwt_token(user):
    user_type = user.__class__.__name__.lower()  # e.g., Admin → "admin"

    payload = {
        'user_id': user.id,
        'type': user_type,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
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

# Decorator to protect routes based on role


# auth.py
def role_required(allowed_roles):
    """
    Decorator to restrict access based on roles, supporting both cookies and headers.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # ✅ Get token from cookies or Authorization header
            token = request.cookies.get('admin_token') or request.headers.get('Authorization')
            if not token:
                return jsonify({"message": "Missing token"}), 401

            try:
                payload = decode_jwt_token(token)
                user_role = payload.get('role')
                if user_role not in allowed_roles:
                    return jsonify({"message": "Unauthorized access"}), 403

            except Exception as e:
                return jsonify({"message": f"Invalid token: {str(e)}"}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator
