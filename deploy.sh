#!/usr/bin/env bash

[ ! -d "data" ] && mkdir data
[ ! -d "tmp/export/work" ] && mkdir -p tmp/export/work
[ ! -d "logs" ] && mkdir logs

cd data
wget https://www.dropbox.com/s/duj0r1ccgjj1olv/PGP3140.json
cd ..tmp/export
wget https://www.dropbox.com/s/qvi229bfdtfxyrw/SEQaBOO_output_template_0730.xlsx
cd ../..

