# Replaced   /anfisa/anfisa/setup --> /anfisa/anfisa because deploy.sh (line 54) does: cp setup/*  $WORKDIR/
## To build:
## In the Repository root:
##  DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker buildx build  --no-cache --tag forome/anfisa:0.8.2 --load -f setup/Dockerfile .
## docker run --rm -p 9081:80 --env-file .env.backend.dev --name anfisa forome/anfisa:0.8.2

FROM python:3.10-slim

ENV NGINX_VERSION=1.23.1
ENV PKG_RELEASE=1~bullseye

RUN set -x \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y gnupg1 ca-certificates \
        zip unzip jq git gcc python3-dev python3-pip python3-venv \
    && apt-get install --no-install-recommends --no-install-suggests -y \
                        nginx \
                        gettext-base \
                        curl \
    && apt-get remove --purge --auto-remove -y && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/nginx.list \
    \
    && if [ -n "$tempDir" ]; then \
        apt-get purge -y --auto-remove \
        && rm -rf "$tempDir" /etc/apt/sources.list.d/temp.list; \
    fi \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

WORKDIR /anfisa/anfisa
COPY . ./
RUN set -x \
    && pip3 install --no-cache-dir -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir supervisor

WORKDIR /anfisa
COPY setup/anfisa.json.template ./
COPY setup/uwsgi.ini ./
COPY setup/igv.dir ./
COPY setup/default.conf.template /etc/nginx/templates/
COPY setup/supervisord.conf /etc/supervisord.conf
COPY setup/entrypoint.sh /entrypoint.sh
COPY setup/entrypoint.d /entrypoint.d
RUN set -eux \
    && chmod +x /entrypoint.sh \
    && chmod +x /entrypoint.d/*.sh

EXPOSE 80
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/usr/local/bin/supervisord" ]
