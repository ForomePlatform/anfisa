#!/bin/sh
# vim:sw=4:ts=4:et

set -e

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