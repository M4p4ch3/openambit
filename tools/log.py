
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
import textwrap
from typing import List
import xml.etree.ElementTree as etree

@dataclass
class Log():

    # Datetime format
    # 2024-04-10T06:22:49
    DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"

    @dataclass
    class Sample():
        type: str
        time: int

        @classmethod
        def from_xml(cls, sample: etree.Element):

            logger = logging.getLogger("Log.Sample::from_xml")

            type = sample.findtext("Type")
            if not type:
                logger.error("Get Type FAILED")
                return None

            if type == Log.PeriodicSample.type:
                return Log.PeriodicSample.from_xml(sample)
            if type == Log.GpsSmallSample.type:
                return Log.GpsSmallSample.from_xml(sample)
            if type == Log.LapInfoSample.type:
                return Log.LapInfoSample.from_xml(sample)
            else:
                logger.debug("Unhandled type %s", type)
                return None

    @dataclass
    class PeriodicSample(Sample):
        type = "periodic"
        utc: datetime | None = None
        cadence: int | None = None
        energy_consumption: int | None = None
        temperature: int | None = None
        altitude: int | None = None
        distance: int | None = None
        speed: int | None = None

        @classmethod
        def from_xml(cls, sample: etree.Element):

            logger = logging.getLogger("Log.PeriodicSample::from_xml")

            time_str = sample.findtext("Time")
            if not time_str:
                logger.error("Get Time FAILED")
                return None
            time = int(time_str)

            utc = None
            utc_str = sample.findtext("UTC")
            if utc_str:
                # UTC format = 2024-04-10T04:22:47.905Z
                # Strip trailling ms
                utc = datetime.strptime(utc_str[:-len(".000Z")], Log.DATETIME_FMT)

            cadence = None
            cadence_str = sample.findtext("Cadence")
            if cadence_str:
                cadence = int(cadence_str)

            energy_consumption = None
            energy_consumption_str = sample.findtext("EnergyConsumption")
            if energy_consumption_str:
                energy_consumption = int(energy_consumption_str)

            temperature = None
            temperature_str = sample.findtext("Temperature")
            if temperature_str:
                temperature = int(temperature_str)

            altitude = None
            altitude_str = sample.findtext("Altitude")
            if altitude_str:
                altitude = int(altitude_str)

            distance = None
            distance_str = sample.findtext("Distance")
            if distance_str:
                distance = int(distance_str)

            speed = None
            speed_str = sample.findtext("Speed")
            if speed_str:
                speed = int(speed_str)

            return Log.PeriodicSample(
                cls.type,
                time,
                utc=utc,
                cadence=cadence,
                energy_consumption=energy_consumption,
                temperature=temperature,
                altitude=altitude,
                distance=distance,
                speed=speed)

    @dataclass
    class GpsSmallSample(Sample):
        type = "gps-small"
        utc: datetime
        latitude: int
        longitude: int

        @classmethod
        def from_xml(cls, sample: etree.Element):

            logger = logging.getLogger("Log.GpsSmallSample::from_xml")

            time_str = sample.findtext("Time")
            if not time_str:
                logger.error("Get Time FAILED")
                return None
            time = int(time_str)

            utc_str = sample.findtext("UTC")
            if not utc_str:
                logger.error("Get UTC FAILED")
                return None
            # UTC format = 2024-04-10T04:22:47.905Z
            # Strip trailling ms
            utc = datetime.strptime(utc_str[:-len(".000Z")], Log.DATETIME_FMT)

            latitude_str = sample.findtext("Latitude")
            if not latitude_str:
                logger.error("Get Latitude FAILED")
                return None
            latitude = int(latitude_str)

            longitude_str = sample.findtext("Longitude")
            if not longitude_str:
                logger.error("Get Longitude FAILED")
                return None
            longitude = int(longitude_str)

            return Log.GpsSmallSample(
                cls.type,
                time,
                utc,
                latitude,
                longitude)

    @dataclass
    class LapInfoSample(Sample):

        @dataclass
        class Lap():
            type: str
            _datetime: datetime
            duration: int
            distance: int

            @classmethod
            def from_xml(cls, lap: etree.Element):

                logger = logging.getLogger("Log.LapInfoSample.Lap::from_xml")

                type = lap.findtext("Type")
                if not type:
                    logger.error("Get Type FAILED")
                    return None

                datetime_str = lap.findtext("DateTime")
                if not datetime_str:
                    logger.error("Get DateTime FAILED")
                    return None
                # UTC format = 2024-04-10T04:22:47.905Z
                # Strip trailling ms
                _datetime = datetime.strptime(datetime_str, Log.DATETIME_FMT)

                duration = None
                duration_str = lap.findtext("Duration")
                if not duration_str:
                    logger.error("Get Duration FAILED")
                    return None
                duration = int(duration_str)

                distance = None
                distance_str = lap.findtext("Distance")
                if not distance_str:
                    logger.error("Get Distance FAILED")
                    return None
                distance = int(distance_str)

                return Log.LapInfoSample.Lap(type, _datetime, duration, distance)

        type = "lap-info"
        lap: Log.LapInfoSample.Lap
        utc: datetime | None = None

        @classmethod
        def from_xml(cls, sample: etree.Element):

            logger = logging.getLogger("Log.LapInfoSample::from_xml")

            time_str = sample.findtext("Time")
            if not time_str:
                logger.error("Get Time FAILED")
                return None
            time = int(time_str)

            utc = None
            utc_str = sample.findtext("UTC")
            if utc_str:
                # UTC format = 2024-04-10T04:22:47.905Z
                # Strip trailling ms
                utc = datetime.strptime(utc_str[:-len(".000Z")], Log.DATETIME_FMT)

            lap_element = sample.find("Lap")
            if not lap_element:
                logger.error("Get Lap FAILED")
                return None

            lap = Log.LapInfoSample.Lap.from_xml(lap_element)
            if not lap:
                logger.error("Log.LapInfoSample.Lap.from_xml FAILED")
                return None

            return Log.LapInfoSample(cls.type, time, lap, utc=utc)

    _datetime: datetime
    activity_type_name: str
    sample_list: List[Log.Sample] = field(default_factory=list)

    @classmethod
    def from_xml(cls, log_element: etree.Element):

        logger = logging.getLogger("Log::from_xml")

        header = log_element.find("Header")
        if not header:
            logger.error("Get Header FAILED")
            return None

        datetime_str = header.findtext("DateTime")
        if not datetime_str:
            logger.error("Get Header/DateTime FAILED")
            return

        activity_type_name = header.findtext("ActivityTypeName")
        if not activity_type_name:
            logger.error("Get Header/ActivityTypeName FAILED")
            return

        _datetime = datetime.strptime(datetime_str, Log.DATETIME_FMT)

        log = Log(_datetime, activity_type_name)

        for sample_element in log_element.iterfind("Samples/Sample"):
            sample = Log.Sample.from_xml(sample_element)
            if sample:
                log.sample_list += [sample]

        return log
