# Replaced   /anfisa/anfisa/setup --> /anfisa/anfisa because deploy.sh (line 54) does: cp setup/*  $WORKDIR/
FROM python:3.7-slim

ENV NGINX_VERSION   1.23.1
ENV PKG_RELEASE     1~bullseye

RUN set -x \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y gnupg1 ca-certificates \
        zip unzip jq git gcc python3-dev python3-pip python3-venv \
    && \
    NGINX_GPGKEY=573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62; \
    found=''; \
    for server in \
        hkp://keyserver.ubuntu.com:80 \
        pgp.mit.edu \
    ; do \
        echo "Fetching GPG key $NGINX_GPGKEY from $server"; \
        apt-key adv --keyserver "$server" --keyserver-options timeout=10 --recv-keys "$NGINX_GPGKEY" && found=yes && break; \
    done; \
    test -z "$found" && echo >&2 "error: failed to fetch GPG key $NGINX_GPGKEY" && exit 1; \
    apt-get remove --purge --auto-remove -y gnupg1 && rm -rf /var/lib/apt/lists/* \
    && dpkgArch="$(dpkg --print-architecture)" \
    && nginxPackages=" \
        nginx=${NGINX_VERSION}-${PKG_RELEASE} \
    " \
    && case "$dpkgArch" in \
        amd64|arm64) \
            echo "deb https://nginx.org/packages/mainline/debian/ bullseye nginx" >> /etc/apt/sources.list.d/nginx.list \
            && apt-get update \
            ;; \
        *) \
            echo "deb-src https://nginx.org/packages/mainline/debian/ bullseye nginx" >> /etc/apt/sources.list.d/nginx.list \
            \
            && tempDir="$(mktemp -d)" \
            && chmod 777 "$tempDir" \
            \
            && savedAptMark="$(apt-mark showmanual)" \
            \
            && apt-get update \
            && apt-get build-dep -y $nginxPackages \
            && ( \
                cd "$tempDir" \
                && DEB_BUILD_OPTIONS="nocheck parallel=$(nproc)" \
                    apt-get source --compile $nginxPackages \
            ) \
            \
            && apt-mark showmanual | xargs apt-mark auto > /dev/null \
            && { [ -z "$savedAptMark" ] || apt-mark manual $savedAptMark; } \
            \
            && ls -lAFh "$tempDir" \
            && ( cd "$tempDir" && dpkg-scanpackages . > Packages ) \
            && grep '^Package: ' "$tempDir/Packages" \
            && echo "deb [ trusted=yes ] file://$tempDir ./" > /etc/apt/sources.list.d/temp.list \
            && apt-get -o Acquire::GzipIndexes=false update \
            ;; \
    esac \
    \
    && apt-get install --no-install-recommends --no-install-suggests -y \
                        $nginxPackages \
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
COPY setup/entrypoint.d/ /entrypoint.d
RUN set -eux \
    && chmod +x /entrypoint.sh \
    && chmod +x /entrypoint.d/*.sh

EXPOSE 80
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/usr/local/bin/supervisord" ]