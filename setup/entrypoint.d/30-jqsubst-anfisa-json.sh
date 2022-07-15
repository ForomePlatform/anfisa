#!/bin/bash

set -e

ME=$(basename $0)

json_subst() {
  echo "$ME: Substitute json values ..."
    # ."igv-dir" = "'"${ANFISA_IGV_DIR}"'" |
  jq '
    ."file-path-def"."ROOT" = "'"${ANFISA_ROOT}"'" |
    ."file-path-def"."SRC" = "'"${ANFISA_SRC}"'" |
    ."file-path-def"."HOME" = "'"${ANFISA_HOME}"'" |
    ."file-path-def"."WORK" = "'"${ANFISA_WORK}"'" |
    ."html-title" = "'"${ANFISA_HTML_TITLE}"'" |
    ."html-base" = "'"${ANFISA_HTML_APP_BASE}"'" |
    ."druid"."vault-prefix" = "'"${ANFISA_DRUID_VAULT_PREFIX}"'" |
    ."druid"."index" = "'"${ANFISA_DRUID_INDEX}"'" |
    ."druid"."coord" = "'"${ANFISA_DRUID_COORD}"'" |
    ."druid"."sql" = "'"${ANFISA_DRUID_SQL}"'" |
    ."druid"."query" = "'"${ANFISA_DRUID_QUERY}"'" |
    ."druid"."copydir" = "'"${ANFISA_DRUID_COPYDIR}"'" |
    ."mongo-host" = "'"${ANFISA_MONGO_HOST}"'" |
    ."mongo-port" = "'"${ANFISA_MONGO_PORT}"'" |
    ."mongo-db" = "'"${ANFISA_MONGO_DB}"'"
    ' \
    anfisa.json > $$.json.tmp && mv $$.json.tmp anfisa.json
}

cd "${ANFISA_ROOT}" && json_subst

exit 0