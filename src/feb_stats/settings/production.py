from .base import *  # noqa

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
