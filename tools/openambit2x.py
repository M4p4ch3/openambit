#!/usr/bin/python

from argparse import ArgumentParser
import logging
import os
import xml.etree.ElementTree as etree

from log import Log
from openambit2gpx import convert_log_to_gpx
from openambit2tcx import convert_log_to_tcx

LOG_LEVEL_DEFAULT = logging.INFO
LOG_LEVEL_VERBOSE = logging.DEBUG
LOG_FMT = "[%(levelname)5s][%(name)12s] %(message)s"

def convert_log_to_x(log_file_path: str, out_dir_path: str = "", average_hr=True):

    logger = logging.getLogger("convert_log_to_x")

    logger.debug("log_file_path = %s", log_file_path)

    log_file_basename = os.path.basename(log_file_path).removesuffix('.log')
    logger.debug("log_file_basename = %s", log_file_basename)

    if not out_dir_path:
        out_dir_path = f"{log_file_path.removesuffix('.log')}"
    logger.debug("out_dir_path = %s", out_dir_path)

    with open(log_file_path, "r") as log_file:
        root = etree.parse(log_file)

        log_element = root.find("Log")
        if not log_element:
            logger.error("Get Log FAILED")
            return

        log = Log.from_xml(log_element)
        if not log:
            logger.error("Get Log.from_xml FAILED")
            return

        if log.activity_type_name == "Aerobics":
            logger.debug("convert_log_to_tcx")
            x_file_path = f"{out_dir_path}/{log_file_basename}.tcx"
            return convert_log_to_tcx(log_file_path, x_file_path)
        else:
            logger.debug("convert_log_to_gpx")
            x_file_path = f"{out_dir_path}/{log_file_basename}.gpx"
            return convert_log_to_gpx(log_file_path, x_file_path, average_hr)

def main():
    parser = ArgumentParser(prog="openambit2x", description="Convert Ambit log file to gpx or tcx")
    parser.add_argument("log_path", help="Path to input log file")
    parser.add_argument('-no-avg-hr', dest='no_avg_hr', action='store_false', default=False,
        help='Do not average hr over 32 heart beats')
    parser.add_argument("-o", "--out", default="", help="Path to output dir")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    log_level = LOG_LEVEL_DEFAULT
    if args.verbose:
        log_level = LOG_LEVEL_VERBOSE
    logging.basicConfig(format=LOG_FMT, level=log_level)

    convert_log_to_x(args.log_path, args.out, args.no_avg_hr)

if __name__ == "__main__":
    main()
