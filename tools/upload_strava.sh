#!/bin/sh

# Convert logs in ~/.openambit/to_upload/ to GPX or TCX and upload them to Strava

ROOT=.

if [ -d tools ] ; then
    ROOT=.
elif [ -d stravauploader ] ; then
    # We are in tools
    ROOT=../
fi

log_list=`ls ~/.openambit/to_upload/*.log`
echo "log_list = $log_list"

out_dir="/home/pache/.openambit/to_upload/"

for log in $log_list ; do
    echo ${ROOT}/tools/openambit2x.py "$log" --out "$out_dir"
    ${ROOT}/tools/openambit2x.py "$log" --out "$out_dir"
done

x_list=`ls ~/.openambit/to_upload/*.*x`
echo "x_list = $x_list"

echo ${ROOT}/tools/stravauploader/strava_uploader.py -l $x_list
${ROOT}/tools/stravauploader/strava_uploader.py -l $x_list
