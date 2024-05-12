#!/usr/bin/python

from argparse import ArgumentParser
from datetime import datetime, timedelta
import logging
import xml.etree.ElementTree as etree

from log import Log
from tcx import Tcx

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

        log_element = root.find("Log")
        if not log_element:
            logger.error("Get Log FAILED")
            return

        log = Log.from_xml(log_element)
        if not log:
            logger.error("Get Log.from_xml FAILED")
            return

        start_datetime = log._datetime
        activity_type_name = log.activity_type_name
        if log.activity_type_name == "Aerobics":
            activity_type_name = "workout"
        activity = Tcx.Activity(id=start_datetime, name=log.activity_name, sport=activity_type_name)

        gps_available = False
        last_time: int | None = None
        distance = 0
        altitude: float | None = None
        position: Tcx.Activity.Lap.Track.Trackpoint.Position | None = None
        heart_rate: int | None = None
        cadence: int | None = None
        lap = Tcx.Activity.Lap()
        track = Tcx.Activity.Lap.Track()

        for sample in log.sample_list:

            if isinstance(sample, Log.PeriodicSample):

                seconds = int(sample.time / 1000)
                _datetime = start_datetime + timedelta(seconds=seconds)

                if sample.distance is not None:
                    distance = sample.distance
                if sample.altitude is not None:
                    altitude = sample.altitude
                if sample.cadence is not None:
                    cadence = sample.cadence

                if not gps_available:
                    if last_time is None or seconds - last_time >= 5:
                        last_time = seconds
                        trackpoint = Tcx.Activity.Lap.Track.Trackpoint(
                            _datetime,
                            distance=distance,
                            altitude=altitude,
                            position=position,
                            heart_rate=heart_rate,
                            cadence=cadence)
                        track.add_trackpoint(trackpoint)

            elif isinstance(sample, Log.GpsSmallSample):
                gps_available = True

                _datetime = sample.utc

                position = Tcx.Activity.Lap.Track.Trackpoint.Position(
                    float(sample.latitude) / 10000000,
                    float(sample.longitude) / 10000000)

                trackpoint = Tcx.Activity.Lap.Track.Trackpoint(
                    _datetime,
                    distance=distance,
                    altitude=altitude,
                    position=position,
                    heart_rate=heart_rate,
                    cadence=cadence)

                track.add_trackpoint(trackpoint)

            elif isinstance(sample, Log.LapInfoSample):

                sample_lap = sample.lap
                if "Interval" not in sample_lap.type:
                    continue

                _datetime = sample_lap._datetime

                # Lap complete
                lap.total_time = sample_lap.duration
                lap.distance = sample_lap.distance
                if "Low" in sample_lap.type:
                    lap.intensity = "Resting"
                if len(track.trackpoint_list) > 0:
                    lap.add_track(track)
                lap.finalize()
                if len(lap.track_list) > 0:
                    activity.add_lap(lap)

                # New lap
                last_time = None
                lap = Tcx.Activity.Lap(_datetime)
                track = Tcx.Activity.Lap.Track()

        # Lap complete
        if len(track.trackpoint_list) > 0:
            lap.add_track(track)
        lap.finalize()
        if len(lap.track_list) > 0:
            activity.add_lap(lap)

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
