#!/bin/sh

# Upload all ..x (GPX or TCX) files in input dir to Strava

ROOT=.
if [ -d tools ] ; then
    ROOT=.
elif [ -d stravauploader ] ; then
    # We are in tools
    ROOT=../
fi

LOG_DIR=$1
if [ "$LOG_DIR" = "" ]; then
    LOG_DIR="$HOME/.openambit/to_upload/"
fi
echo "LOG_DIR = $LOG_DIR"

x_list=`ls $LOG_DIR/*.*x`
echo "x_list = [$x_list]"

echo ${ROOT}/tools/stravauploader/strava_uploader.py -l $x_list
${ROOT}/tools/stravauploader/strava_uploader.py -l $x_list
