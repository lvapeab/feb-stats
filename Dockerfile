FROM ubuntu:18.04
RUN apt-get update -y && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.7 python3.7-dev python3-pip git curl wget

RUN curl -LO "https://github.com/bazelbuild/bazelisk/releases/download/v1.1.0/bazelisk-linux-amd64"  && \
        mkdir -p "/usr/bin/"  && \
        mv bazelisk-linux-amd64 "/usr/bin/bazel"  && \
        chmod +x "/usr//bin/bazel"

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2

RUN python3 -m pip install --user --upgrade pip
RUN python3 -m pip install --user -U keyrings.alt
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3

COPY . /code/
WORKDIR /code