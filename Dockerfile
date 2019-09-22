FROM python:3.7-stretch

ENV PROJECT_HOME /data/projects/anfisa-app
ENV PROJECT_WORKDIR /data/projects/anfisa-data
ENV PATH $PROJECT_HOME/bin:$PATH
ENV PYTHONPATH $PROJECT_HOME
RUN mkdir -p $PROJECT_HOME

COPY . $PROJECT_HOME
WORKDIR $PROJECT_HOME
RUN pip install -r ./requirements.txt
RUN sed -i 's#${HOME}/../a-setup#/data/projects/anfisa-data/#' anfisa.json
RUN sed -i '/"mongo-db": "Anfisa",/a\    "mongo-host": "mongo",' anfisa.json
