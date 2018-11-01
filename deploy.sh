#!/usr/bin/env bash

repo=`pwd`
target=$repo
if [ -f .inst_dir ] ; then
    target=`cat .inst_dir`
fi

read -p "Installation directory: ${target}? (y/n)" response
if [ $response != "y" ] && [ $response != "Y" ] ; then
    read -p "Type directory: " target
fi

read -p "Install Anfisa into ${target}? (y/n)" response
if [ $response != "y" ] && [ $response != "Y" ] ; then
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
[ ! -d "tmp/export/work" ] && mkdir -p tmp/export/work
[ ! -d "logs" ] && mkdir logs

cd data
rm *
wget https://www.dropbox.com/s/duj0r1ccgjj1olv/PGP3140.json
cd ../tmp/export
[ ! -f SEQaBOO_output_template_0730.xlsx ] && wget https://www.dropbox.com/s/qvi229bfdtfxyrw/SEQaBOO_output_template_0730.xlsx

cd ../..
echo "Updating configuration in anfisa.json"
hostname=`hostname`
sed  "s#../a-setup#$target#" anfisa.json > anfisa_$hostname.json

cd $repo
echo "Run anfisa: python hserver.py $target/anfisa_$hostname.json"
