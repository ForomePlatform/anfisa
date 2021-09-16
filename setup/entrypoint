#!/bin/bash
export COUNT_FILES=$(ls -A /anfisa/a-setup/ | wc -l)
if [ ${COUNT_FILES} -le 2 ] ; then
    mkdir -p /anfisa/a-setup/{data,logs,vault,export/work,ui}
fi

exec "$@"
