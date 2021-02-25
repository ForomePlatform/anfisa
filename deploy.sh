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
				chmod -R a+rwx $ASETUP
			fi
			;;
		--druidwork=*)
			DRUID=${flag#*=}
			if [ ! -d "$DRUID" ]; then
				mkdir -p $DRUID
				mkdir -p $DRUID/airflow 
				mkdir -p $DRUID/coordinator
				mkdir -p $DRUID/data
				mkdir -p $DRUID/historical-var
				mkdir -p $DRUID/middlemanager
				mkdir -p $DRUID/router
				mkdir -p $DRUID/broker
				chmod -R a+rwx $DRUID
			fi
			;;
		--airflowwork=*)
			AIRFLOW=${flag#*=}
			if [ ! -d "$AIRFLOW" ]; then
				mkdir -p $AIRFLOW
				mkdir -p $AIRFLOW/data
				chmod -R a+rwx $AIRFLOW
			fi
			;;
		--hostip=*) HOSTIP=${flag#*=};;
		*)
			usage
			exit
			;;
	esac
done

if [ ! -z "$ASETUP" ] && [ ! -z "$DRUID" ] && [ ! -z "$AIRFLOW" ] && [ ! -z "$HOSTIP" ] ; then

chmod -R a+rwx $ASETUP
chmod -R a+rwx $ASETUP/../data
chmod -R a+rwx $DRUID
chmod -R a+rwx $AIRFLOW


sed "s#ASETUP_PATH#${ASETUP}#g" setup/docker-compose.yml.template | sed "s#DRUID_WORK#${DRUID}#g" - | sed "s#AIRFLOW_WORK#${AIRFLOW}#g" - > docker-compose.yml

sed "s#HOST_IP#${HOSTIP}#g" anfisa.json.template > anfisa.json
sed "s#HOST_IP#${HOSTIP}#g" setup/environment.template > environment

docker-compose build
docker-compose up -d
docker ps

else
echo ERROR! All parameters are required!
fi

