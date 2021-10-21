#!/bin/bash
for d in /anfisa/a-setup/{data,logs,vault,export/work,ui} ; do
    [ ! -d $d ] && mkdir -p $d
done
if [ ! -f /anfisa/a-setup/export/SEQaBOO_output_template_20190317.xlsx ]  ; then
  pushd /anfisa/a-setup/export
  curl -L -O https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx
  popd
fi

if [ ! -z ${ANFISA_COORD_HOST+z} ] && [ ! -z ${ANFISA_ROUTER_HOST+z} ] && [ ! -z ${ANFISA_MONGO_HOST+z} ] ;
then
    sed "s#anfisa6-coordinator#${ANFISA_COORD_HOST}#g" /anfisa/anfisa.json | sed "s#anfisa6-router#${ANFISA_ROUTER_HOST}#g" | sed "s#anfisa6-mongo#${ANFISA_MONGO_HOST}#g" -  > /anfisa/anfisa.json
fi

exec "$@"