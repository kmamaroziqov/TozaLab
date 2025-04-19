# firebase_service.py
import firebase_admin
from firebase_admin import credentials, messaging

# ✅ Load Firebase credentials
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_config/firebase-config.json')
    firebase_admin.initialize_app(cred)

def send_push_notification(fcm_token, title, body):
    """
    Sends a push notification via Firebase Cloud Messaging (FCM).
    
    Args:
        fcm_token (str): The FCM device token.
        title (str): The notification title.
        body (str): The notification body.
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token,
        )
        response = messaging.send(message)
        print(f'Successfully sent notification: {response}')
    except Exception as e:
        print(f'Failed to send notification: {e}')


def subscribe_user_to_topic(fcm_token, topic='default-topic'):
    """Subscribes a user's FCM token to a topic."""
    try:
        response = messaging.subscribe_to_topic([fcm_token], topic)
        print(f'Subscribed user to topic {topic}: {response.success_count} success')
    except Exception as e:
        print(f'Failed to subscribe user to topic: {e}')


def broadcast_to_topic(title, body, topic='default-topic'):
    """Broadcasts a notification to all users subscribed to a topic."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
    )
    try:
        response = messaging.send(message)
        print(f'Successfully broadcasted to topic {topic}: {response}')
    except Exception as e:
        print(f'Failed to broadcast to topic {topic}: {e}')