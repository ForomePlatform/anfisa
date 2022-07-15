#!/bin/bash

set -e

ME=$(basename $0)

json_subst() {
  local anfisa_conf_template="${ANFISA_SRC}/anfisa.json.template"
  local anfisa_conf="${ANFISA_SRC}/anfisa.json"
  if [ -f "$anfisa_conf" ]; then
    echo "$ME: ERROR: $anfisa_conf exists, exiting ..."
    return 0
  fi
  echo "$ME: Substitute json values ..."
    # ."file-path-def"."ROOT" = "'"${ANFISA_ROOT}"'" |
    # ."file-path-def"."HOME" = "'"${ANFISA_HOME}"'" |
  jq '
    ."file-path-def"."WORK" = "'"${ANFISA_WORK}"'" |
    ."file-path-def"."SRC" = "'"${ANFISA_SRC}"'" |
    ."html-title" = "'"${ANFISA_HTML_TITLE}"'" |
    ."igv-dir" = "'"${ANFISA_IGV_DIR}"'" |
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
    "$anfisa_conf_template" > "$anfisa_conf"
    # anfisa.json > $$.json.tmp && mv $$.json.tmp anfisa.json
}

json_subst

exit 0