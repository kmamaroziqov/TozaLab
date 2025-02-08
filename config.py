import os
import stripe
from dotenv import load_dotenv
load_dotenv()
# Set your Stripe API keys
 # Replace with your actual publishable key

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")