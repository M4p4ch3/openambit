#!/bin/bash

# Convert all logs in given directory to gpx or tcx, if not already existing

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
echo "SCRIPT_DIR = $SCRIPT_DIR"

LOG_DIR=$1
if [ "$LOG_DIR" = "" ]; then
    LOG_DIR="$HOME/.openambit"
fi
echo "LOG_DIR = $LOG_DIR"

OUT_DIR=$2
if [ "$OUT_DIR" = "" ]; then
    OUT_DIR="$LOG_DIR"
fi
echo "OUT_DIR = $OUT_DIR"

log_list=`ls $LOG_DIR/*.log`
for log in $log_list ; do
    echo "log = $log"

    if [[ -f "${log/.log/.gpx}" || -f "${log/.log/.tcx}" ]]; then
        echo "gpx or tcx file already exists, skipping"
    else
        echo $SCRIPT_DIR/openambit2x.py "$log" --out "$OUT_DIR"
        $SCRIPT_DIR/openambit2x.py "$log" --out "$OUT_DIR"
    fi
done
