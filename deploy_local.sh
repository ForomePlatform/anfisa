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
[ ! -d "export/work" ] && mkdir -p export/work
[ ! -d "logs" ] && mkdir logs
[ ! -d "vault" ] && mkdir vault

rm vault/*
if [ ! -d data/docs ] ; then
  cd data || exit
  rm -r *
  curl -O -L https://forome-project-bucket.s3.eu-central-1.amazonaws.com/v6/pgp3140_wgs_hlpanel.zip
  unzip pgp3140_wgs_hlpanel.zip
  cd ..
fi

if [ ! -f export/SEQaBOO_output_template_20190317.xlsx ] ; then
  cd export || exit
  curl -O -L https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx
  cd ..
fi

echo "Updating configuration in anfisa.json"
hostname=`hostname`
sed  's#/anfisa/a-setup#WOWOWOWO#' ${repo}/setup/anfisa.json.template \
  | sed "s#WOWOWOWO#$target#" \
  | sed "s#PATH_TO_SOURCE#$repo#" \
  | sed "s/HOST_IP/127.0.0.1/" \
  |  sed "s/3041/8190/" > anfisa_$hostname.json

pip3 install wheel # apparently we need this before other requirements
pip3 install -r ${repo}/requirements.txt
pip3 install -e git+https://github.com/ForomePlatform/forome_misc_tools.git#egg=forome-tools

echo "Loading Sample Dataset"
echo "PYTHONPATH=$repo python3 -u -m app.storage -c $target/anfisa_$hostname.json -m create -f -k ws -i data/pgp3140_wgs_hlpanel.cfg PGP3140"
PYTHONPATH=$repo python3 -u -m app.storage -c $target/anfisa_$hostname.json -m create -f -k ws -i data/pgp3140_wgs_hlpanel.cfg PGP3140

cd $repo || exit
echo "Run anfisa: env PYTHONPATH="." python3 app/run.py $target/anfisa_$hostname.json"
echo "Then point your browser to: http://localhost:8190/dir"
