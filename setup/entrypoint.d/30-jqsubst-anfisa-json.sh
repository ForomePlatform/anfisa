#!/bin/bash

set -e

ME=$(basename $0)

json_subst() {
  local anfisa_conf_template="/anfisa/anfisa.json.template"
  local anfisa_conf="/anfisa/anfisa.json"
  if [[ -f "$anfisa_conf" ]]; then
    echo "$ME: ERROR: $anfisa_conf exists, exiting ..."
    return 0
  fi
  echo "$ME: Substitute json values ..."
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
    ."mongo-host" = "'"${ANFISA_MONGOHOST}"'" |
    ."mongo-db" = "'"${ANFISA_MONGODB}"'" |
    ."mongo-port" = '"${ANFISA_MONGOPORT}"'
    ' \
    "$anfisa_conf_template" > "$anfisa_conf"
  if [[ ! -z "${ANFISA_DRUIDCOPYDIR}" ]]; then
    jq '."druid"."copydir" = "'"${ANFISA_DRUIDCOPYDIR}"'"' anfisa.json > $$.json.tmp && mv $$.json.tmp anfisa.json
  fi
}

json_subst

exit 0