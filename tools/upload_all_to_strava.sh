#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
echo "SCRIPT_DIR = $SCRIPT_DIR"

LOG_DIR=$1
if [ "$LOG_DIR" = "" ]; then
    LOG_DIR="$HOME/.openambit"
fi
echo "LOG_DIR = $LOG_DIR"

log_list=`ls $LOG_DIR/*.gpx`
echo log_list = ${log_list}

for log in $log_list ; do
    echo "log = $log"

    echo "$SCRIPT_DIR/stravauploader/strava_uploader.py -l $log"
    $SCRIPT_DIR/stravauploader/strava_uploader.py -l $log
done
