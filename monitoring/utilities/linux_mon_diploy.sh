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
    -n|--name)
    NAME="$2"
    shift # past argument
    shift # past value
    ;;
esac
done

echo IP OF MANAGER        = "${IP}"
echo PORT OPEN ON MANAGER = "${PORT}"
echo NAME OF INSTANCE     = "${NAME}"

git clone https://github.com/brianmc95/cloud-fyp.git

mkdir monitor

cwd=$(pwd)
MACHINE_ID=$(cat) /etc/machine-id

if [ -z "$MACHINE_ID" ]
then
    MACHINE_ID =

cp ${cwd}/cloud-fyp/monitoring/Monitor.py ${cwd}/monitor/

rm -rf cloud-fyp

echo "*/5 * * * * python3 ${cwd}/monitor/Monitor.py --ip ${IP} -p ${PORT} --id ${ID} -n ${NAME}" > mon_cron_job

crontab mon_cron_job
