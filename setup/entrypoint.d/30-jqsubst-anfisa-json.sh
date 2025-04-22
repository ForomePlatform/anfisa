#!/bin/bash

set -e

ME=$(basename "$0")

json_subst() {
  local anfisa_conf_template="/anfisa/anfisa.json.template"
  local anfisa_conf="/anfisa/anfisa.json"

  # Check if configuration file already exists
  if [[ -f "$anfisa_conf" ]]; then
    echo "$ME: $anfisa_conf exists, skip substitute"
    return 0
  fi

  echo "$ME: Substitute json values from $anfisa_conf_template to $anfisa_conf"

  jq --arg ANFISA_WORK "$ANFISA_WORK" \
     --arg ANFISA_SRC "$ANFISA_SRC" \
     --arg ANFISA_HTML_TITLE "$ANFISA_HTML_TITLE" \
     --arg ANFISA_HTML_APP_BASE "$ANFISA_HTML_APP_BASE" \
     --arg ANFISA_IGVDIR "$ANFISA_IGVDIR" \
     --arg ANFISA_DRUIDVAULTPREFIX "$ANFISA_DRUIDVAULTPREFIX" \
     --arg ANFISA_DRUIDINDEX "$ANFISA_DRUIDINDEX" \
     --arg ANFISA_DRUIDCOORD "$ANFISA_DRUIDCOORD" \
     --arg ANFISA_DRUIDSQL "$ANFISA_DRUIDSQL" \
     --arg ANFISA_DRUIDQUERY "$ANFISA_DRUIDQUERY" \
     --arg ANFISA_MONGOHOST "$ANFISA_MONGOHOST" \
     --arg ANFISA_MONGODB "$ANFISA_MONGODB" \
     --argjson ANFISA_MONGOPORT "$ANFISA_MONGOPORT" \
     '
     # Use gsub to strip any accidental extraneous quotes
     ."file-path-def"."WORK" = ($ANFISA_WORK | gsub("^\"|\"$"; "")) |
     ."file-path-def"."SRC" = ($ANFISA_SRC | gsub("^\"|\"$"; "")) |
     ."html-title" = ($ANFISA_HTML_TITLE | gsub("^\"|\"$"; "")) |
     ."html-base" = ($ANFISA_HTML_APP_BASE | gsub("^\"|\"$"; "")) |
     ."igv-dir" = ($ANFISA_IGVDIR | gsub("^\"|\"$"; "")) |
     ."druid"."vault-prefix" = ($ANFISA_DRUIDVAULTPREFIX | gsub("^\"|\"$"; "")) |
     ."druid"."index" = ($ANFISA_DRUIDINDEX | gsub("^\"|\"$"; "")) |
     ."druid"."coord" = ($ANFISA_DRUIDCOORD | gsub("^\"|\"$"; "")) |
     ."druid"."sql" = ($ANFISA_DRUIDSQL | gsub("^\"|\"$"; "")) |
     ."druid"."query" = ($ANFISA_DRUIDQUERY | gsub("^\"|\"$"; "")) |
     ."mongo-host" = ($ANFISA_MONGOHOST | gsub("^\"|\"$"; "")) |
     ."mongo-db" = ($ANFISA_MONGODB | gsub("^\"|\"$"; "")) |
     ."mongo-port" = $ANFISA_MONGOPORT
     ' "$anfisa_conf_template" > "$anfisa_conf"

  # Handle conditional setting for additional optional items
  if [[ -n "${ANFISA_DRUIDCOPYDIR}" ]]; then
    jq --arg ANFISA_DRUIDCOPYDIR "$ANFISA_DRUIDCOPYDIR" \
       '."druid"."copydir" = ($ANFISA_DRUIDCOPYDIR | gsub("^\"|\"$"; ""))' "$anfisa_conf" > $$.json.tmp && mv $$.json.tmp "$anfisa_conf"
  fi
}

json_subst

exit 0
