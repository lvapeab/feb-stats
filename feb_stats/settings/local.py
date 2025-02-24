from .base import *  # noqa


CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "https://localhost",
    "https://127.0.0.1",
]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "127.0.0.1:8000",
]


CORS_ALLOWED_ORIGINS: list[str] = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "127.0.0.1",
]

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_HOST = None
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
