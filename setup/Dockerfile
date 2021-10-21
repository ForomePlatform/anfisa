# Replaced   /anfisa/anfisa/setup --> /anfisa/anfisa because deploy.sh (line 54) does: cp setup/*  $WORKDIR/
FROM python:3.7
WORKDIR /anfisa
RUN bash -c 'mkdir -p /anfisa/anfisa && mkdir -p /anfisa/a-setup/ && mkdir -p /data/'

COPY . /anfisa/anfisa/
RUN cd /anfisa/anfisa/ && pip3 install -r requirements.txt && pip3 install supervisor && pip3 install -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools 
RUN cd /anfisa/anfisa/setup && mv anfisa.json.docker /anfisa/anfisa.json && mv entrypoint.sh /usr/bin/entrypoint.sh && chmod +x /usr/bin/entrypoint.sh
ENV ANFISA_HOME=/anfisa/anfisa
ENV ANFISA_WORK=/anfisa/a-setup
ENV ANFISA_ROOT=/anfisa
ENV ANFISA_HTML_APP_BASE=/anfisa/app
ENV ANFISA_HTML_BASE=/anfisa
RUN apt-get update && apt-get install -y nginx 
RUN cd /anfisa/anfisa/setup && mv default.nginx /etc/nginx/sites-available/default && mv supervisord.conf /etc/supervisord.conf && mv uwsgi.ini /anfisa/uwsgi.ini


EXPOSE 80
ENTRYPOINT [ "entrypoint.sh" ]