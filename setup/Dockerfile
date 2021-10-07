FROM python:3.7
WORKDIR /anfisa
RUN bash -c 'mkdir -p /anfisa/anfisa && mkdir -p /anfisa/a-setup/ && mkdir -p /anfisa/a-setup/{data,logs,vault,export/work,ui}'

COPY . /anfisa/anfisa/
RUN cd /anfisa/anfisa/ && pip3 install -r requirements.txt && pip3 install supervisor && pip3 install -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools
#RUN cd /anfisa/a-setup/data/ && curl -O -L https://anfisa.forome.dev/distrib/datasets/PGP3140.json.gz
RUN cd /anfisa/anfisa/ && mv anfisa.json.docker /anfisa/anfisa.json
RUN ln -sf /dev/stdout /anfisa/a-setup/logs/anfisa.log
ENV ANFISA_HOME=/anfisa/anfisa
ENV ANFISA_WORK=/anfisa/a-setup
ENV ANFISA_ROOT=/anfisa
ENV ANFISA_HTML_APP_BASE=/anfisa/app
ENV ANFISA_HTML_BASE=/anfisa
RUN apt-get update && apt-get install -y nginx 
RUN mv /anfisa/anfisa/default /etc/nginx/sites-available/default && mv /anfisa/anfisa/supervisord.conf /etc/supervisord.conf && mv /anfisa/anfisa/uwsgi.ini /anfisa/uwsgi.ini

#COPY --from=buildstage /repo/dist /var/www/html/anfisa/

EXPOSE 80
CMD ["/usr/local/bin/supervisord"]

