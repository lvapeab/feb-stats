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
    apt-get install -y  curl wget

# System deps:
RUN python3 -m pip install --upgrade pip pipx

ENV PATH=/root/.local/bin:$PATH

RUN pipx install poetry

WORKDIR /code

COPY poetry.lock pyproject.toml /code/

RUN poetry install --no-root --no-dev


ENV PYTHONPATH="/code:$PYTHONPATH"

COPY . .

EXPOSE 80 80

CMD ["poetry", "run", "gunicorn", "feb_stats.web.webapp:app"]
