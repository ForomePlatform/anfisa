#!/bin/bash

set -e

ME=$(basename $0)

echo "$ME: Create directories"

for d in {/anfisa/a-setup/{data,logs,vault,export/work,ui},/data} ; do
  [ ! -d "$d" ] && mkdir -p "$d"
done

echo "$ME: Download export template"

if [ ! -f /anfisa/a-setup/export/SEQaBOO_output_template_20190317.xlsx ]  ; then
  pushd /anfisa/a-setup/export || exit
  curl -fsSLO https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx
  popd
fi

# if [ ! -z ${ANFISA_COORD_HOST+z} ] && [ ! -z ${ANFISA_ROUTER_HOST+z} ] && [ ! -z ${ANFISA_MONGO_HOST+z} ] && [ $(grep -q -e 'anfisa7-' /anfisa/anfisa.json) ] ; then
#   sed "s#anfisa7-coordinator#${ANFISA_COORD_HOST}#g" /anfisa/anfisa.json | sed "s#anfisa7-router#${ANFISA_ROUTER_HOST}#g" | sed "s#anfisa7-mongo#${ANFISA_MONGO_HOST}#g" - > /anfisa/anfisa.json
# fi