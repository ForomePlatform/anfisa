#!/usr/bin/env bash

repo=`pwd`
target=$repo
if [ -f .inst_dir ] ; then
    target=`cat .inst_dir`
fi

read -p "Installation directory: ${target}? (y/n)" response
if [ "$response" != "y" ] && [ "$response" != "Y" ] ; then
    read -p "Type directory: " target
fi

read -p "Install Anfisa into ${target}? (y/n)" response
if [ "$response" != "y" ] && [ "$response" != "Y" ] ; then
    echo "Installation aborted"
    return 1 2> /dev/null || exit 1
fi

if [ $repo != $target ] ; then
    echo Setting up $target
    mkdir -p $target
    cp $repo/anfisa.json $target
    echo $target > .inst_dir
    cd $target
else
    echo "Installing into repository directory"
fi


[ ! -d "data" ] && mkdir data
[ ! -d "tmp/export/work" ] && mkdir -p export/work
[ ! -d "logs" ] && mkdir logs
[ ! -d "vault" ] && mkdir vault

rm vault/*
cd data
rm *
curl -O -L https://forome-project-bucket.s3.eu-central-1.amazonaws.com/v6/pgp3140_wgs_hlpanel.zip
unzip pgp3140_wgs_hlpanel.zip
# cd ../tmp/export
# [ ! -f SEQaBOO_output_template_20190317.xlsx ] && wget https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx

cd ..
echo "Updating configuration in anfisa.json"
hostname=`hostname`
sed  's#${HOME}/../a-setup#WOWOWOWO#' anfisa.json | sed "s#WOWOWOWO#$target#" > anfisa_$hostname.json
echo "Loading Sample Dataset"
echo "PYTHONPATH=$repo python3 -m -u app.storage -c $target/anfisa_$hostname.json -m create -f -k ws -i data/PGP3140.json.gz PGP3140"
PYTHONPATH=$repo python3 -m app.storage -c $target/anfisa_$hostname.json -m create -f -k ws -s data/pgp3140_wgs_hlpanel.cfg PGP3140

cd $repo
echo "Run anfisa: env PYTHONPATH="." python3 app/run.py $target/anfisa_$hostname.json"
echo "Then point your browser to: http://localhost:8190/dir"
