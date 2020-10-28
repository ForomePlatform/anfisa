#!/bin/sh

usage()
{
cat << EOF
	Usage: $0 --workdir=/path/to/workdir/for/anfisa/0.6/ --hostip=A.B.C.D 
EOF
}


for flag in "$@"
do
	case $flag in
		--workdir=*) 
			WORKDIR=${flag#*=}
			if [ ! -d "$WORKDIR" ]; then
				mkdir -p $WORKDIR
				chmod a+rwx $WORKDIR
			fi
			ASETUP=$WORKDIR/a-setup
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
			if [ ! -d "$ASETUP/../data" ] ; then
				mkdir -p $ASETUP/../data
			fi
			DRUID=$WORKDIR/druid
			if [ ! -d "$DRUID" ]; then
				mkdir -p $DRUID
				mkdir -p $DRUID/airflow
				mkdir -p $DRUID/coordinator
				mkdir -p $DRUID/data
				mkdir -p $DRUID/historical-var
				mkdir -p $DRUID/middlemanager
				mkdir -p $DRUID/router
				chmod -R a+rwx $DRUID
			fi
			AIRFLOW=$WORKDIR/airflow
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


sed "s#ASETUP_PATH#${ASETUP}#g" docker-compose.yml.template | sed "s#DRUID_WORK#${DRUID}#g" - | sed "s#AIRFLOW_WORK#${AIRFLOW}#g" - > docker-compose.yml

sed "s#HOST_IP#${HOSTIP}#g" anfisa.json.template > anfisa.json
sed "s#HOST_IP#${HOSTIP}#g" environment.template > environment

docker-compose build
docker-compose up -d
docker ps

else
echo ERROR! All parameters are required!
fi

