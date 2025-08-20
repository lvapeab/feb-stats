FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100


RUN apt-get update -y && \
    apt-get install -y  curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --upgrade pip pipx && \
    pipx install uv

ENV PATH=/root/.local/bin:$PATH

WORKDIR /code

COPY uv.lock pyproject.toml README.md /code/
COPY scripts/* /code/scripts/

RUN uv sync --frozen

ENV PYTHONPATH="/code:$PYTHONPATH"

COPY . .

RUN uv run python manage.py collectstatic --noinput --settings=src.feb_stats.settings.production

EXPOSE 8080

CMD ["uv", "run", "gunicorn", \
     "feb_stats.wsgi:application", \
     "--env", "DJANGO_SETTINGS_MODULE=src.feb_stats.settings.production", \
     "--bind", "0.0.0.0:8080", \
     "--timeout", "300" \
     ]
