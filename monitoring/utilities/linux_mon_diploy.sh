#!/usr/bin/env bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -ip)
    IP="$2"
    shift # past argument
    shift # past value
    ;;
    -p|--port)
    PORT="$2"
    shift # past argument
    shift # past value
    ;;
    -id)
    ID="$2"
    shift # past argument
    shift # past value
    ;;
    -pv|--provider)
    PROVIDER="$2"
    shift # past argument
    shift # past value
    ;;
esac
done

echo IP OF MANAGER        = "${IP}"
echo PORT OPEN ON MANAGER = "${PORT}"
echo ID OF MACHINE        = "${ID}"
echo PROVIDER             = "${PROVIDER}"

git clone https://github.com/brianmc95/cloud-fyp.git

mkdir monitor
touch monitor/prev_report.json

cwd=$(pwd)

cp ${cwd}/cloud-fyp/monitoring/Monitor.py ${cwd}/monitor/

rm -rf cloud-fyp

pip3 install requests

echo "*/5 * * * * python3 ${cwd}/monitor/Monitor.py -ip ${IP} -p ${PORT} -id ${ID} --provider ${PROVIDER}" > monitor/mon_cron_job

crontab mon_cron_job
