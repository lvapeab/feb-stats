FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VIRTUALENVS_IN_PROJECT=false \
  POETRY_NO_INTERACTION=1


RUN apt-get update -y && \
    apt-get install -y  curl wget && \
    rm -rf /var/lib/apt/lists/*

# System deps:
RUN python3 -m pip install --upgrade pip pipx

ENV PATH=/root/.local/bin:$PATH

RUN pipx install poetry

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
COPY scripts/* /code/scripts/

RUN poetry install --no-interaction --no-ansi --only main

ENV PYTHONPATH="/code:$PYTHONPATH"

COPY . .

RUN poetry run python manage.py collectstatic --noinput --settings=feb_stats.settings.production

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "feb_stats.wsgi:application", "--env", "DJANGO_SETTINGS_MODULE=feb_stats.settings.production"]
