# auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta
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

# Decorator to protect routes based on role


def role_required(allowed_roles):
    """
    Decorator to restrict access to specific roles.
    :param allowed_roles: List of roles that are allowed to access the route.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the token from the Authorization header
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"message": "Missing token"}), 401

            try:
                # Decode the JWT token
                payload = decode_jwt_token(token)

                # Check if the user's role is in the allowed roles
                user_role = payload.get('role')
                if user_role not in allowed_roles:
                    return jsonify({"message": "Unauthorized access"}), 403

            except Exception as e:
                # Handle token decoding errors
                return jsonify({"message": str(e)}), 401

            # If everything is fine, call the original function
            return f(*args, **kwargs)

        return decorated_function
    return decorator