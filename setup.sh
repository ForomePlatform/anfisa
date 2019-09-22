#!/bin/sh

mkdir -p $PROJECT_WORKDIR/data $PROJECT_WORKDIR/export/work $PROJECT_WORKDIR/logs $PROJECT_WORKDIR/vault

cd $PROJECT_WORKDIR/data
echo "Loading Sample Dataset"
curl -O -L https://www.dropbox.com/s/8u4kwp5m3px6tcz/PGP3140.json.gz

echo "python -m app.storage -c $PROJECT_HOME/anfisa.json -m create -f -k ws -s PGP3140.json.gz PGP3140"
python -m app.storage -c $PROJECT_HOME/anfisa.json -m create -f -k ws -s PGP3140.json.gz PGP3140
