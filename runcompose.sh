#!/bin/sh

usage()
{
cat << EOF
	Usage: $0 --asetup=/path/to/asetup --druidwork=/path/to/druid/workdir/ --airflowwork=/path/to/airflow/workdir/ --hostip=A.B.C.D 
EOF
}


for flag in "$@"
do
	case $flag in
		--asetup=*) 
			ASETUP=${flag#*=}
			if [ ! -d "$ASETUP" ]; then
				mkdir -p $ASETUP
				mkdir -p $ASETUP/data/examples
				mkdir -p $ASETUP/vault
				mkdir -p $ASETUP/ui
				mkdir -p $ASETUP/export
				mkdir -p $ASETUP/logs
				mkdir -p $ASETUP/../data
				sudo chmod -R a+rx $ASETUP
			fi
			;;
		--druidwork=*)
			DRUID=${flag#*=}
			if [ ! -d "$DRUID" ]; then
				mkdir -p $DRUID
				mkdir -p $DRUID/{airflow, broker, coordinator, data, historical-var, middlemanager, router}
			fi
			;;
		--airflowwork=*)
			AIRFLOW=${flag#*=}
			if [ ! -d "$AIRFLOW" ]; then
				mkdir -p $AIRFLOW
				mkdir -p $AIRFLOW/data
			fi
			;;
		--hostip=*) HOSTIP=${flag#*=};;
		*)
			usage
			exit
			;;
	esac
done
sed "s#ASETUP_PATH#${ASETUP}#g" docker-compose.yml.template | sed "s#DRUID_WORK#${DRUID}#g" - | sed "s#AIRFLOW_WORK#${AIRFLOW}#g" - > docker-compose.yml

sed "s#HOST_IP#${HOSTIP}#g" anfisa.json.template > anfisa.json

docker-compose build
docker-compose up -d
docker ps
