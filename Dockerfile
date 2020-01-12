FROM alpine:3.10

LABEL maintainer="TheMeanCanEHdian"

# environment variables
ENV PS1="$(whoami)@$(hostname):$(pwd)$ "
ENV SALTTOTASTE_DOCKER=True
ENV TZ=UTC

RUN \
  echo "**** install build packages ****" && \
  apk add --no-cache --virtual=build-dependencies \
  autoconf \
  automake \
  curl \
  g++ \
  gcc \
  libffi-dev \
  linux-headers \
  make \
  openssl-dev \
  python3-dev \
  tar && \
  echo "**** install runtime packages ****" && \
  apk add --no-cache \
  py-pip \
  python3

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN \
  pip3 install -r requirements.txt && \
  # Workaround for Flask-WhooshAlchemy3 having SQLALchemy 1.1.13 in its requirements.txt
  pip3 install sqlalchemy --upgrade

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "saltToTaste.py", "--datadir", "/config" ]

VOLUME /config
EXPOSE 8100
