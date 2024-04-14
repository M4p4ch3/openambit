#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
echo "SCRIPT_DIR = $SCRIPT_DIR"

LOG_DIR=$1
if [ "$LOG_DIR" = "" ]; then
    LOG_DIR="$HOME/.openambit"
fi
echo "LOG_DIR = $LOG_DIR"

log_list=`ls $LOG_DIR/*.log`
echo log_list = ${log_list}

for log in $log_list ; do
    echo "log     = $log"

    log_out="$LOG_DIR/$(basename $log .log).gpx"
    echo "log_out = $log_out"

    echo "$SCRIPT_DIR/openambit2gpx.py -out \"$log_out\" \"$log\""
    $SCRIPT_DIR/openambit2gpx.py -out "$log_out" "$log"
done
