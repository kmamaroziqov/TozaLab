# application.py
from flask import Flask
import sentry_sdk
import redis
from extensions import db, admin  # ✅ Shared extensions
import os
from dotenv import load_dotenv

load_dotenv()

sentry_sdk.init(
    dsn="https://8c6516dc2b417ecaebd32ef6b8777c35@o4508822984720384.ingest.de.sentry.io/4508822993895504",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Connect to Redis (default host: localhost, port: 6379)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# ✅ Initialize extensions ONCE
db.init_app(app)
admin.init_app(app)