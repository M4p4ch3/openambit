#!/usr/bin/python

from argparse import ArgumentParser
from datetime import datetime, timedelta
import logging
import xml.etree.ElementTree as etree

from tcx import Tcx

# Datetime format in log file
# 2024-04-10T06:22:49
DATETIME_FMT_LOG = "%Y-%m-%dT%H:%M:%S"

SEC_PER_MIN = 60
MIN_PER_HOUR = 60
SEC_PER_HOUR = SEC_PER_MIN * MIN_PER_HOUR

LOG_LEVEL_DEFAULT = logging.INFO
LOG_LEVEL_VERBOSE = logging.DEBUG
LOG_FMT = "[%(levelname)5s][%(name)12s] %(message)s"

def convert_log_to_tcx(log_file_path: str, tcx_file_path: str = ""):

    logger = logging.getLogger("convert_log_to_tcx")

    if not tcx_file_path:
        tcx_file_path = f"{log_file_path.removesuffix('.log')}.tcx"
    logger.debug("tcx_file_path = %s", tcx_file_path)

    with open(log_file_path, "r") as log_file:
        root = etree.parse(log_file)

        tcx = Tcx()

        header = root.find("Log/Header")
        if not header:
            logger.error("Get Log/Header FAILED")
            return

        _datetime = header.findtext("DateTime")
        if not _datetime:
            logger.error("Get Log/Header/DateTime FAILED")
            return

        activity_type_name = header.findtext("ActivityTypeName")
        if not activity_type_name:
            logger.error("Get Log/Header/ActivityTypeName FAILED")
            return

        start_datetime = datetime.strptime(_datetime, DATETIME_FMT_LOG)
        activity = Tcx.Activity(activity_type_name, start_datetime)

        position = None
        altitude = 0
        distance = 0
        heart_rate = 0
        lap = Tcx.Activity.Lap()
        track = Tcx.Activity.Lap.Track()

        for sample in root.iterfind("Log/Samples/Sample"):
            type = sample.findtext("Type")
            if not type:
                logger.error("Get Log/Samples/Sample/Type FAILED")
                continue

            utc = sample.findtext("UTC")
            if utc:
                # UTC format = 2024-04-10T04:22:47.905Z
                # Strip trailling ms
                _datetime = datetime.strptime(utc[:-len(".000Z")], DATETIME_FMT_LOG)
            else:
                # Rely on elapsed time instead
                time = sample.findtext("Time")
                if not time:
                    logger.error("Get Log/Samples/Sample/Time FAILED")
                    continue
                _datetime = start_datetime + timedelta(seconds=int(int(time)/1000))
                logger.debug("time = %s", _datetime)

            if type == "periodic":

                altitude_str = sample.findtext("Altitude")
                if altitude_str:
                    altitude = int(altitude_str)

                distance_str = sample.findtext("Distance")
                if distance_str:
                    distance = int(distance_str)

                heart_rate_str = sample.findtext("HeartRate")
                if heart_rate_str:
                   heart_rate = int(heart_rate_str)

                trackpoint = Tcx.Activity.Lap.Track.Trackpoint(
                    _datetime,
                    position,
                    float(altitude),
                    float(distance),
                    heart_rate)

                track.add_trackpoint(trackpoint)

            elif "gps-" in type:

                latitude = sample.findtext("Latitude")
                if not latitude:
                    logger.error("Get Log/Samples/Sample/Latitude FAILED")
                    continue

                longitude = sample.findtext("Longitude")
                if not longitude:
                    logger.error("Get Log/Samples/Sample/Longitude FAILED")
                    continue

                position = Tcx.Activity.Lap.Track.Trackpoint.Position(
                    float(latitude) / 10000000,
                    float(longitude) / 10000000)

                trackpoint = Tcx.Activity.Lap.Track.Trackpoint(
                    _datetime,
                    position,
                    float(altitude),
                    float(distance),
                    heart_rate)

                track.add_trackpoint(trackpoint)

            elif type == "lap-info":

                lap_element = sample.find("Lap")
                if not lap_element:
                    logger.error("Get Log/Samples/Sample/Lap FAILED")
                    continue

                lap_type = lap_element.findtext("Type")
                if not lap_type:
                    logger.error("Get Log/Samples/Sample/Lap/Type FAILED")
                    continue

                duration = lap_element.findtext("Duration")
                if not duration:
                    logger.error("Get Log/Samples/Sample/Lap/Duration FAILED")
                    continue

                distance_str = lap_element.findtext("Distance")
                if not distance_str:
                    logger.error("Get Log/Samples/Sample/Lap/Distance FAILED")
                    continue

                if lap_type == "Start":
                    # New lap
                    lap = Tcx.Activity.Lap(_datetime)
                    track = Tcx.Activity.Lap.Track()
                elif lap_type == "Pause" or "Interval" in lap_type:
                    # Lap complete
                    lap.total_time = int(duration)
                    lap.distance = int(distance_str)
                    if "Low" in lap_type:
                        lap.intensity = "Resting"
                    if len(track.trackpoint_list) > 0:
                        lap.add_track(track)
                    lap.finalize()
                    activity.add_lap(lap)
                else:
                    logger.warning("Unhandled lap type %s", lap_type)

        tcx.add_activity(activity)
        tcx.export(tcx_file_path)

def main():
    parser = ArgumentParser(prog="openambit2tcx", description="Convert Ambit log file to tcx")
    parser.add_argument("log_path", help="Path to input log file")
    parser.add_argument("-o", "--out", default="", help="Path to output tcx file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    log_level = LOG_LEVEL_DEFAULT
    if args.verbose:
        log_level = LOG_LEVEL_VERBOSE
    logging.basicConfig(format=LOG_FMT, level=log_level)

    convert_log_to_tcx(args.log_path, args.out)

if __name__ == "__main__":
    main()
