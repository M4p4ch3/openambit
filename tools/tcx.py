
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import textwrap
from typing import List

DATETIME_NONE = datetime(1, 1, 1)

def format_txt(txt: str):
    txt = textwrap.dedent(txt.removeprefix("\n"))
    while txt.endswith(" "):
        txt.removesuffix(" ")
    return txt

@dataclass
class Tcx():

    # 2011-07-10T09:52:40Z
    DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

    @dataclass
    class Activity():

        @dataclass
        class Lap():

            @dataclass
            class Track():

                @dataclass
                class Trackpoint():

                    @dataclass
                    class Position():

                        lat: float
                        long: float

                        def to_xml(self):
                            return format_txt(f"""
                                <Position>
                                    <LatitudeDegrees>{self.lat}</LatitudeDegrees>
                                    <LongitudeDegrees>{self.long}</LongitudeDegrees>
                                </Position>
                                """)

                    time: datetime
                    distance: float = 0.0
                    altitude: float | None = None
                    position: Tcx.Activity.Lap.Track.Trackpoint.Position | None = None
                    heart_rate: int | None = None
                    cadence: int | None = None

                    def to_xml(self):

                        ret = format_txt(f"""
                            <Trackpoint>
                                <Time>{self.time.strftime(Tcx.DATETIME_FMT)}</Time>
                                <DistanceMeters>{self.distance}</DistanceMeters>
                            """)

                        if self.altitude is not None:
                            ret += textwrap.indent(format_txt(f"""
                                    <AltitudeMeters>{self.altitude}</AltitudeMeters>
                                """), "    ")

                        if self.position:
                            ret += textwrap.indent(self.position.to_xml(), "    ")

                        if self.heart_rate is not None:
                            ret += textwrap.indent(format_txt(f"""
                                <HeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
                                    <Value>{self.heart_rate}</Value>
                                </HeartRateBpm>
                            """), "    ")

                        if self.cadence is not None:
                            ret += textwrap.indent(format_txt(f"""
                                <Extensions>
                                    <TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2" CadenceSensor="">
                                        <RunCadence>{self.cadence}</RunCadence>
                                    </TPX>
                                </Extensions>
                                """), "    ")

                        ret += format_txt(f"""
                            </Trackpoint>
                            """)

                        return ret

                trackpoint_list: List[Tcx.Activity.Lap.Track.Trackpoint] = field(default_factory=list)

                def add_trackpoint(self, trackpoint: Tcx.Activity.Lap.Track.Trackpoint):
                    self.trackpoint_list += [trackpoint]

                def to_xml(self):
                    ret = format_txt(f"""
                        <Track>
                        """)
                    for trackpoint in self.trackpoint_list:
                        ret += textwrap.indent(trackpoint.to_xml(), "    ")
                    ret += format_txt(f"""
                        </Track>
                        """)
                    return ret

            start_time: datetime = DATETIME_NONE
            total_time: float = 0.0
            distance: float = 0.0
            max_speed: float = 0.0
            calories: int = 0
            avg_heart_rate: int = 0
            max_heart_rate: int = 0
            intensity: str = "Active"
            trigger_method: str = "Manual"
            track_list: List[Tcx.Activity.Lap.Track] = field(default_factory=list)

            def add_track(self, track: Tcx.Activity.Lap.Track):
                self.track_list += [track]

            def finalize(self):

                if self.start_time == DATETIME_NONE:
                    if len(self.track_list) > 0:
                        if len(self.track_list[0].trackpoint_list) > 0:
                            self.start_time = self.track_list[0].trackpoint_list[0].time

                if self.total_time == 0.0:
                    if len(self.track_list) > 0:
                        if len(self.track_list[0].trackpoint_list) > 0:
                            end_time = self.track_list[-1].trackpoint_list[-1].time
                            self.total_time = (end_time - self.start_time).seconds

                heart_rate_list: List[int] = []
                for track in self.track_list:
                    for trackpoint in track.trackpoint_list:
                        if trackpoint.heart_rate is not None:
                            heart_rate_list += [trackpoint.heart_rate]
                if self.max_heart_rate == 0:
                    if len(heart_rate_list) > 0:
                        self.max_heart_rate = max(heart_rate_list)
                if self.avg_heart_rate == 0:
                    if len(heart_rate_list) > 0:
                        self.avg_heart_rate = int(self.max_heart_rate / len(heart_rate_list))

            def to_xml(self):
                ret = format_txt(f"""
                    <Lap StartTime="{self.start_time.strftime(Tcx.DATETIME_FMT)}">
                        <TotalTimeSeconds>{self.total_time}</TotalTimeSeconds>
                        <DistanceMeters>{self.distance}</DistanceMeters>
                        <MaximumSpeed>{self.max_speed}</MaximumSpeed>
                        <Calories>{self.calories}</Calories>
                        <AverageHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
                            <Value>{self.avg_heart_rate}</Value>
                        </AverageHeartRateBpm>
                        <MaximumHeartRateBpm xsi:type="HeartRateInBeatsPerMinute_t">
                            <Value>{self.max_heart_rate}</Value>
                        </MaximumHeartRateBpm>
                        <Intensity>{self.intensity}</Intensity>
                        <TriggerMethod>{self.trigger_method}</TriggerMethod>
                    """)
                for track in self.track_list:
                    ret += textwrap.indent(track.to_xml(), "    ")
                ret += format_txt(f"""
                    </Lap>
                    """)
                return ret

        id: datetime
        name: str
        sport: str
        lap_list: List[Tcx.Activity.Lap] = field(default_factory=list)

        def add_lap(self, lap: Tcx.Activity.Lap):
            self.lap_list += [lap]

        def to_xml(self):
            ret = format_txt(f"""
                <Activity Sport="{self.sport}">
                    <Id>{self.id.strftime(Tcx.DATETIME_FMT)}</Id>
                    <Name>{self.name}</Name>
                """)
            for lap in self.lap_list:
                ret += textwrap.indent(lap.to_xml(), "    ")
            ret += format_txt(f"""
                </Activity>
                """)
            return ret

    activity_list: List[Tcx.Activity] = field(default_factory=list)

    def add_activity(self, activity: Tcx.Activity):
        self.activity_list += [activity]

    def to_xml(self):
        ret = format_txt(f"""
            <?xml version="1.0" standalone="no" ?>
            <TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">

            <Activities>
            """)
        for activity in self.activity_list:
            ret += textwrap.indent(activity.to_xml(), "    ")
        ret += format_txt(f"""
            </Activities>
            """)
        return ret

    def export(self, out_file_path: str):
        with open(out_file_path, "w") as out_file:
            out_file.write(self.to_xml())
