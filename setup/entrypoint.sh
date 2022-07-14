#!/bin/bash
for d in {/anfisa/a-setup/{data,logs,vault,export/work,ui},/data} ; do
    [ ! -d $d ] && mkdir -p $d
done

if [ ! -f /anfisa/a-setup/export/SEQaBOO_output_template_20190317.xlsx ]  ; then
  pushd /anfisa/a-setup/export
  curl -L -O https://www.dropbox.com/s/4dvunn3dusqc636/SEQaBOO_output_template_20190317.xlsx
  popd
fi

if [ ! -z ${ANFISA_COORD_HOST+z} ] && [ ! -z ${ANFISA_ROUTER_HOST+z} ] && [ ! -z ${ANFISA_MONGO_HOST+z} ] ;
then
    sed "s#anfisa7-coordinator#${ANFISA_COORD_HOST}#g" /anfisa/anfisa.json | sed "s#anfisa7-router#${ANFISA_ROUTER_HOST}#g" | sed "s#anfisa7-mongo#${ANFISA_MONGO_HOST}#g" -  > /anfisa/anfisa.json
fi

echo "$0: Looking for shell scripts in /entrypoint.d/"
find "/entrypoint.d/" -follow -type f -print | sort -V | while read -r f; do
    case "$f" in
        *.sh)
            if [ -x "$f" ]; then
                echo "$0: Launching $f";
                "$f"
            else
                # warn on shell scripts without exec bit
                echo "$0: Ignoring $f, not executable";
            fi
            ;;
        *) echo "$0: Ignoring $f";;
    esac
done

exec "$@"