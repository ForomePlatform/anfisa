FROM python:3.7
WORKDIR /anfisa
RUN bash -c 'mkdir -p /anfisa/anfisa && mkdir -p /anfisa/a-setup/ && mkdir -p /anfisa/a-setup/{data,logs,vault,export/work,ui} && mkdir -p /data/'

COPY . /anfisa/anfisa/
RUN cd /anfisa/anfisa/ && pip3 install -r requirements.txt && pip3 install supervisor && pip3 install -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools
#RUN cd /anfisa/a-setup/data/ && curl -O -L https://anfisa.forome.dev/distrib/datasets/PGP3140.json.gz
RUN cd /anfisa/anfisa/setup/ && mv anfisa.json.docker /anfisa/anfisa.json
ENV ANFISA_HOME=/anfisa/anfisa
ENV ANFISA_WORK=/anfisa/a-setup
ENV ANFISA_ROOT=/anfisa
ENV ANFISA_HTML_APP_BASE=/anfisa/app
ENV ANFISA_HTML_BASE=/anfisa
RUN apt-get update && apt-get install -y nginx 
RUN mv /anfisa/anfisa/setup/default /etc/nginx/sites-available/default && mv /anfisa/anfisa/setup/supervisord.conf /etc/supervisord.conf && mv /anfisa/anfisa/setup/uwsgi.ini /anfisa/uwsgi.ini

#COPY --from=buildstage /repo/dist /var/www/html/anfisa/

EXPOSE 80
CMD ["/usr/local/bin/supervisord"]

