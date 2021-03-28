FROM python:3.7.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN apt-get update -y && \
    apt-get install -y  curl wget

RUN python3 -m pip install --user -U keyrings.alt && \
    curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3

COPY pyproject.toml /

ENV PATH="/root/.poetry/bin:$PATH" \
    PYTHONPATH="/code:$PYTHONPATH" \
    FLASK_ENV="development" \
    FLASK_APP="python/web/webapp.py"

RUN poetry update

COPY ./ /code/
WORKDIR /code

EXPOSE 80 50001


CMD ["poetry", "run", "python", "-m", "flask", "run", "--port", "80", "--host", "0.0.0.0"]