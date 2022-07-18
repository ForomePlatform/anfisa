#!/bin/bash

set -e

ME=$(basename $0)

json_subst() {
  local anfisa_conf_template="/anfisa/anfisa.json.template"
  local anfisa_conf="/anfisa/anfisa.json"
  if [ -f "$anfisa_conf" ]; then
    echo "$ME: ERROR: $anfisa_conf exists, exiting ..."
    return 0
  fi
  echo "$ME: Substitute json values ..."
    # ."file-path-def"."HOME" = "'"${ANFISA_HOME}"'" |
    # ."file-path-def"."ROOT" = "'"${ANFISA_ROOT}"'" |
  jq '
    ."file-path-def"."WORK" = "'"${ANFISA_WORK}"'" |
    ."file-path-def"."SRC" = "'"${ANFISA_SRC}"'" |
    ."html-title" = "'"${ANFISA_HTML_TITLE}"'" |
    ."html-base" = "'"${ANFISA_HTML_APP_BASE}"'" |
    ."druid"."vault-prefix" = "'"${ANFISA_DRUIDVAULTPREFIX}"'" |
    ."druid"."index" = "'"${ANFISA_DRUIDINDEX}"'" |
    ."druid"."coord" = "'"${ANFISA_DRUIDCOORD}"'" |
    ."druid"."sql" = "'"${ANFISA_DRUIDSQL}"'" |
    ."druid"."query" = "'"${ANFISA_DRUIDQUERY}"'" |
    ."druid"."copydir" = "'"${ANFISA_DRUIDCOPYDIR}"'" |
    ."mongo-host" = "'"${ANFISA_MONGOHOST}"'" |
    ."mongo-port" = '"${ANFISA_MONGOPORT}"' |
    ."mongo-db" = "'"${ANFISA_MONGODB}"'"
    ' \
    "$anfisa_conf_template" > "$anfisa_conf"
    # anfisa.json > $$.json.tmp && mv $$.json.tmp anfisa.json
}

json_subst

exit 0