from .base import *  # noqa
import os
from dotenv import load_dotenv

DEBUG = False

CSRF_TRUSTED_ORIGINS = [
    "https://feb-stats-11741086955.europe-west9.run.app",
    "https://feb-stats-hmruu3u6mq-od.a.run.app",
]

ALLOWED_HOSTS = [
    "feb-stats-11741086955.europe-west9.run.app",
    "feb-stats-hmruu3u6mq-od.a.run.app",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


load_dotenv()
DATABASES = {
    "default": {
        "ENGINE": "django_cockroachdb",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "26257"),
        "OPTIONS": {"sslmode": "require", "sslrootcert": os.getenv("DB_ROOT_CERT"), "connect_timeout": 10},
    }
}
