FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apt-get update -y && \
    apt-get install -y  curl wget

# System deps:
RUN python3 -m pip install --upgrade pip pipx

ENV PATH=/root/.local/bin:$PATH

RUN pipx install pipenv

WORKDIR /code

COPY Pipfile Pipfile.lock /code/

RUN pipenv install --deploy


ENV PYTHONPATH="/code:$PYTHONPATH"

COPY . .

EXPOSE 80 80

CMD ["pipenv", "run", "gunicorn", "feb_stats.web.webapp:app"]
