FROM ubuntu:latest
RUN ["mkdir", "-p", "/app"]
WORKDIR /app
COPY init.sql .
COPY init_db.sh .
RUN chmod +x init_db.sh

RUN apt-get update && apt-get install -y mysql-client wget

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

CMD dockerize -wait tcp://db:3306 -timeout 300s -wait-retry-interval 1s ./init_db.sh