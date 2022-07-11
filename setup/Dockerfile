# Replaced   /anfisa/anfisa/setup --> /anfisa/anfisa because deploy.sh (line 54) does: cp setup/*  $WORKDIR/
FROM python:3.7
ENV ANFISA_HOME=/anfisa/anfisa
ENV ANFISA_WORK=/anfisa/a-setup
ENV ANFISA_ROOT=/anfisa
ENV ANFISA_HTML_APP_BASE=/anfisa/app
ENV ANFISA_HTML_BASE=/anfisa
RUN set -eux \
    && apt-get update \
	&& apt-get install --no-install-recommends -y nginx \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /anfisa
# RUN set -eux \
#     && bash -c 'mkdir -p {anfisa/{anfisa,a-setup},/data}'
COPY setup/anfisa.json.docker ./anfisa.json
COPY setup/uwsgi.ini ./uwsgi.ini
# COPY setup/default.nginx /etc/nginx/conf.d/anfisa.conf
COPY setup/default.nginx /etc/nginx/sites-enabled/default
COPY setup/supervisord.conf /etc/supervisord.conf
COPY setup/entrypoint.sh /usr/bin/entrypoint.sh
RUN set -eux \
    && chmod +x /usr/bin/entrypoint.sh
WORKDIR /anfisa/anfisa
COPY . ./
RUN pip3 install -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools
RUN pip3 install -r requirements.txt
RUN pip3 install supervisor
WORKDIR /anfisa
EXPOSE 80
ENTRYPOINT [ "/usr/bin/entrypoint.sh" ]
CMD [ "/usr/local/bin/supervisord" ]