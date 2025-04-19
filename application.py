from flask import Flask
from flask_migrate import Migrate
from extensions import db, admin
import redis
import sentry_sdk
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Initialize Sentry first
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=True,
    traces_sample_rate=1.0,
    _experiments={"continuous_profiling_auto_start": True}
)

# ✅ Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# ✅ Initialize extensions
db.init_app(app)
admin.init_app(app)
migrate = Migrate(app, db)

# ✅ Redis (if needed)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)