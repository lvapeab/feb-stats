FROM python:3.7.9-slim-buster

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

RUN apt-get update -y && \
    apt-get install -y  curl wget

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml /

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ENV PATH="/root/.poetry/bin:$PATH" \
    PYTHONPATH="/code:$PYTHONPATH"

RUN poetry install

COPY ./ /code/
WORKDIR /code

EXPOSE 80 50001

CMD ["poetry", "run", "gunicorn", "--umask", "4", "--bind", "0.0.0.0:80", "feb_stats.web.webapp:app"]