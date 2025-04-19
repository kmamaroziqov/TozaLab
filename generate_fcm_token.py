# generate_fcm_token.py
import firebase_admin
from firebase_admin import credentials, messaging

# ✅ Load Firebase credentials
cred = credentials.Certificate('firebase_config/firebase-config.json')
firebase_admin.initialize_app(cred)

def generate_test_token():
    try:
        # Generate a registration token (Test Token)
        test_token = messaging.Token('test-device-token')
        print(f'Generated Test FCM Token: {test_token}')
        return test_token
    except Exception as e:
        print(f'Error generating test token: {e}')

# Run the function
generate_test_token()
