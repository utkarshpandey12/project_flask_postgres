import json
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENABLE_CORS = os.getenv("ENABLE_CORS", "false").lower() == "true"
SITE_NAME = "API"
URL_PREFIX = os.getenv("URL_PREFIX")

# Flask-SQLAlchemy
DB_SECRET = json.loads(os.getenv("DB_SECRET"))
DB_USER = DB_SECRET.get("username")
DB_PASSWORD = DB_SECRET.get("password")
DB_HOST = DB_SECRET.get("host")
DB_PORT = DB_SECRET.get("port")
DB_NAME = DB_SECRET.get("dbname")

if DB_USER and DB_PASSWORD and DB_HOST and DB_PORT:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME,
    )
elif DB_USER and DB_PASSWORD:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s/%s" % (
        DB_USER,
        DB_PASSWORD,
        DB_NAME,
    )
elif DB_HOST and DB_PORT:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://%s:%s/%s" % (
        DB_HOST,
        DB_PORT,
        DB_NAME,
    )
else:
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2:///%s" % (DB_NAME,)

SQLALCHEMY_ECHO = DEBUG
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis
REDIS_JOBS_HOST = os.getenv("REDIS_JOBS_HOST")
REDIS_JOBS_PORT = int(os.getenv("REDIS_JOBS_PORT"))
REDIS_JOBS_DB = int(os.getenv("REDIS_JOBS_DB"))

# Maximum allowed age of sessions in seconds. Set to 0 to allow sessions to
# live forever.
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "0"))

# S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", None)
S3_BUCKET_NAME_PRIVATE = os.getenv("S3_BUCKET_NAME_PRIVATE")
S3_BUCKET_NAME_PUBLIC = os.getenv("S3_BUCKET_NAME_PUBLIC")
S3_SIGNED_URL_EXPIRY = 60  # seconds
