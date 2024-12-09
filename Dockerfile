FROM python:3.8.12-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.8.4

RUN apt-get update -y && \
    apt-get install -y  curl wget

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code
COPY pyproject.toml /code/

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ENV PATH="/root/.poetry/bin:$PATH" \
    PYTHONPATH="/code:$PYTHONPATH"

COPY . .

EXPOSE 80 80

CMD ["poetry", "run", "gunicorn", "--umask", "4", "--bind", "0.0.0.0:80", "feb_stats.web.webapp:app"]