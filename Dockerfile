FROM python:3.7-alpine
MAINTAINER Nayara Caetano <nayara.caetanopinheiro@gmail.com>

ENV PYTHONUNBUFFERED=1

# Enable timezone support
ENV TZ=America/Sao_Paulo
RUN apk --no-cache add tzdata

# Install dependencies
COPY requirements.txt /
RUN apk add --no-cache \
        postgresql-dev && \
    apk add --no-cache --virtual .build-deps \
        gcc libc-dev \
        git && \
    pip install -r /requirements.txt && \
    apk del .build-deps

COPY entrypoint.sh /

# Add application data
WORKDIR /var/www
COPY . /var/www

# Create non-privileged user
RUN adduser -Ds /bin/sh lottery && \
    mkdir -p \
        /var/www/staticfiles \
        /var/log/lottery_api && \
    chown -R lottery:lottery \
        /var/www \
        /var/log/lottery_api
USER lottery

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
CMD ["run"]
