#!/bin/bash

usage()
{
cat << EOF
	Usage: $0 --workdir=/path/to/workdir/for/anfisa/0.6/ 
EOF
}


for flag in "$@"
do
	case $flag in
		--workdir=*) 
			WORKDIR=${flag#*=}
			echo WORKDIR=$WORKDIR
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

  cp setup/*  $WORKDIR/
  cp -R app doc export int_ui requirements.txt LICENSE README.md $WORKDIR/

  pushd $ASETUP/data/examples || exit
  if [ ! -d docs ] ; then
    curl -L -O https://forome-project-bucket.s3.eu-central-1.amazonaws.com/v6/pgp3140_wgs_hlpanel.zip
    unzip pgp3140_wgs_hlpanel.zip
  fi

  cd $WORKDIR || exit
  sed "s#ASETUP_PATH#${ASETUP}#g" docker-compose.yml.template | sed "s#DRUID_WORK#${DRUID}#g" -  > docker-compose.yml

  docker-compose build
  docker-compose up -d
  docker ps

  docker exec -it anfisa6_docker sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -u -m app.storage -c /anfisa/anfisa.json -m create --reportlines 200 -f -k ws -i /anfisa/a-setup/data/examples/pgp3140_wgs_hlpanel.cfg PGP3140_HL_GENES'
  docker exec -it anfisa6_docker sh -c 'PYTHONPATH=/anfisa/anfisa/ python3 -u -m app.storage -c /anfisa/anfisa.json -m create --reportlines 200 -f -k xl -i /anfisa/a-setup/data/examples/pgp3140_wgs_hlpanel.cfg XL_PGP3140_HL_GENES'

  popd || exit

  echo "Open URL http://localhost:9010/anfisa/app/dir"
else
  echo ERROR! All parameters are required!
  usage
fi

