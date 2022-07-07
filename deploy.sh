#!/bin/bash

usage()
{
cat << EOF
	Usage: $0 --workdir=/path/to/workdir/for/anfisa/0.7/ 
EOF
}


for flag in "$@"
do
	case $flag in
		--workdir=*) 
			WORKDIR=${flag#*=}
			echo WORKDIR=$WORKDIR
			if [[ $WORKDIR != /* ]]; then
                                echo "ERROR! $WORKDIR is a relative path. Specify absolute path to the working directory."
                                usage
                                exit 1
                        fi
			if [ ! -d "$WORKDIR" ]; then
				mkdir -p $WORKDIR
				chmod a+rwx $WORKDIR
			fi
			ASETUP=$WORKDIR/a-setup
			echo A-Setup=$ASETUP
			if [ ! -d "$ASETUP" ]; then
				mkdir -p $ASETUP
				mkdir -p $ASETUP/data/examples
				mkdir -p $ASETUP/vault
				mkdir -p $ASETUP/ui
				mkdir -p $ASETUP/export
				mkdir -p $ASETUP/logs
				chmod -R a+rwx $ASETUP
			fi
			if [ ! -d "$ASETUP/../data" ] ; then
				mkdir -p $ASETUP/../data
			fi
			DRUID=$WORKDIR/druid
			echo DRUID=$DRUID
			if [ ! -d "$DRUID" ]; then
				mkdir -p $DRUID
				mkdir -p $DRUID/coordinator
				mkdir -p $DRUID/data
				mkdir -p $DRUID/historical-var
				mkdir -p $DRUID/middlemanager
				mkdir -p $DRUID/router
				chmod -R a+rwx $DRUID
			fi
			;;
	esac
done

if [ ! -z "$ASETUP" ] && [ ! -z "$DRUID" ] ; then
  chmod -R a+rwx $ASETUP
  chmod -R a+rwx $DRUID

  cp -R setup app doc export int_ui requirements.txt setup.py LICENSE README.md $WORKDIR/

  pushd $ASETUP/data/examples || exit
  if [ ! -d pgp3140_wgs_hlpanel/docs ] ; then
    curl -L -O https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/pgp3140_wgs_hlpanel.zip
	mkdir pgp3140_wgs_hlpanel
    unzip pgp3140_wgs_hlpanel.zip -d ./pgp3140_wgs_hlpanel
  fi

  pushd $ASETUP/data || exit
  if [ ! -f gene_db.js ] ; then
    curl -L -O https://forome-dataset-public.s3.us-south.cloud-object-storage.appdomain.cloud/gene_db.zip
    unzip gene_db.zip
  fi

  cd $WORKDIR || exit
  sed "s#ASETUP_PATH#${ASETUP}#g" setup/docker-compose.yml.template | sed "s#DRUID_WORK#${DRUID}#g" > docker-compose.yml

  docker compose build
  docker compose up -d
  docker ps

  docker exec -it anfisa7 sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -m app.adm_mongo -c /anfisa/anfisa.json -m GeneDb /anfisa/a-setup/data/gene_db.js'

  docker exec -it anfisa7 sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -u -m app.storage -c /anfisa/anfisa.json -m create --reportlines 200 -f -k ws -i /anfisa/a-setup/data/examples/pgp3140_wgs_hlpanel/pgp3140_wgs_hlpanel.cfg PGP3140_HL_GENES'
  docker exec -it anfisa7 sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -u -m app.storage -c /anfisa/anfisa.json -m create --reportlines 200 -f -k xl -i /anfisa/a-setup/data/examples/pgp3140_wgs_hlpanel/pgp3140_wgs_hlpanel.cfg XL_PGP3140_HL_GENES'

  popd || exit

  echo "Open URL http://localhost:9010/anfisa/app/dir - The internal UI"
  echo "Open URL http://localhost:3000 - Anfisa's graphical interface"
else
  echo ERROR! All parameters are required!
  usage
fi
sudo docker exec -d anfisa7 sed -i '59 i \\t\tadd_header 'Access-Control-Allow-Origin' '*' always;' /etc/nginx/conf.d/anfisa.conf
sudo docker exec -d anfisa7 nginx -s reload