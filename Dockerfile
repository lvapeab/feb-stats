FROM ubuntu:18.04
RUN apt-get update -y && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.7 python3.7-dev python3-pip git curl wget

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.5 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN curl https://bazel.build/bazel-release.pub.gpg | apt-key add - && \
    echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list && \
    apt-get update -y && \
    apt-get install -y bazel


RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2

RUN python3 -m pip install --user --upgrade pip
RUN python3 -m pip install --user --upgrade keyrings.alt
RUN python3 -m pip install "poetry==$POETRY_VERSION"

COPY ./data /data
COPY . /code/
WORKDIR /code

EXPOSE 50001
CMD ["bazel",  "run",  "//python/service:server", "--", "-local"]