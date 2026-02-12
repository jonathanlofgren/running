from __future__ import annotations

import enum
import re

import click

DISTANCE_UNITS = {
    "feet": 0.3048,
    "foot": 0.3048,
    "yard": 0.9144,
    "yards": 0.9144,
    "m": 1,
    "meter": 1,
    "meters": 1,
    "k": 1000,
    "km": 1000,
    "kilometer": 1000,
    "mile": 1609.344,
    "miles": 1609.344,
    "marathon": 42195,
    "half": 42195 / 2,
    "half-marathon": 42195 / 2,
}
SECOND = 1
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
TIME_UNITS = {
    "s": SECOND,
    "sec": SECOND,
    "secs": SECOND,
    "second": SECOND,
    "seconds": SECOND,
    "m": MINUTE,
    "min": MINUTE,
    "mins": MINUTE,
    "minute": MINUTE,
    "minutes": MINUTE,
    "h": HOUR,
    "hour": HOUR,
    "hours": HOUR,
    "d": DAY,
    "day": DAY,
    "days": DAY,
    "w": WEEK,
    "week": WEEK,
    "weeks": WEEK,
}
PACES = {"kipchoge": 42195 / (2 * HOUR + 1 * MINUTE + 39), "bolt": 100 / 9.58}


class Mode(enum.Enum):
    PACE = 0
    DISTANCE = 1
    TIME = 2
    NOT_ENOUGH = 3
    TOO_MUCH = 4


Meters = float
Seconds = float
MetersPerSecond = float


@click.command()
@click.option(
    "--pace",
    "-p",
    help="Running pace, for example '5:30', '4min/mile', '3min/km', '8:00/mile' etc.",
)
@click.option(
    "--distance", "-d", help="Running distance, for example '10k', '800m', 'marathon', '1mile' etc."
)
@click.option("--time", "-t", help="Running time, for example '1:35:00', '2h', '100sec' etc")
@click.option(
    "--unit",
    "-u",
    help="Default distance unit when omitted and for result (default is kilometer).",
    default="km",
)
def running(time: str, distance: str, pace: str, unit: str):
    mode = identify_mode(time, distance, pace)

    if mode == Mode.PACE:
        seconds = parse_time(time)
        meters = parse_distance(distance, unit)
        speed: MetersPerSecond = meters / seconds
        output_line("Required pace:", format_pace(speed, unit), "/" + unit)

    elif mode == Mode.DISTANCE:
        speed = parse_pace(pace, unit)
        seconds = parse_time(time)
        meters: Meters = speed * seconds
        output_line("Travelled distance:", format_distance(meters, unit), unit)

    elif mode == Mode.TIME:
        speed = parse_pace(pace, unit)
        meters = parse_distance(distance, unit)
        seconds: Seconds = meters / speed
        output_line("Elapsed time:", format_seconds(seconds), "[H:]MM:SS")

    elif mode == Mode.NOT_ENOUGH:
        error("You need to give atleast two of time, distance or pace.")

    elif mode == Mode.TOO_MUCH:
        error("You provided time, distance and pace. Try omitting one.")


def output_line(pre: str, bolded: str, post: str) -> None:
    click.echo(f"{pre} ", nl=False)
    click.secho(bolded, bold=True, nl=False)
    click.echo(f" {post}")


def error(message: str) -> None:
    click.secho(message, fg="red")
    click.echo("See running --help for further instructions.")


def identify_mode(time: str | None, distance: str | None, pace: str | None) -> Mode:

    def given(*metrics):
        return all(metric is not None for metric in metrics)

    if given(time, distance, pace):
        return Mode.TOO_MUCH
    elif given(time, pace):
        return Mode.DISTANCE
    elif given(distance, pace):
        return Mode.TIME
    elif given(distance, time):
        return Mode.PACE
    else:
        return Mode.NOT_ENOUGH


def parse_time(time: str) -> Seconds:
    if ":" in time:  # example '2:30:01'
        parts = [float(t) for t in time.split(":")]
        return sum(n * secs for n, secs in zip(reversed(parts), (1, 60, 3600)))

    if time in TIME_UNITS:
        return TIME_UNITS[time]

    num, unit = extract_num_and_unit(time)
    return TIME_UNITS[unit or "s"] * num


def parse_distance(distance: str, default_unit: str) -> Meters:
    if distance in DISTANCE_UNITS:
        return DISTANCE_UNITS[distance]

    num, unit = extract_num_and_unit(distance)
    return DISTANCE_UNITS[unit or default_unit] * num


def parse_pace(pace: str, default_unit: str) -> MetersPerSecond:
    if pace in PACES:
        return PACES[pace]

    if "/" in pace:
        time_str, distance_str = pace.split("/")
        time = parse_time(time_str)
        distance = parse_distance(distance_str, default_unit)
    else:
        time = parse_time(pace)
        distance = DISTANCE_UNITS[default_unit]

    return distance / time


def extract_num_and_unit(num_and_unit) -> tuple[float, str | None]:
    match = re.match(r"(\d*\.\d+|\d+)([\w-]*)\Z", num_and_unit)
    if not match:
        raise ValueError(f"Invalid unit {num_and_unit}")
    return float(match.group(1)), match.group(2)


def format_pace(speed: MetersPerSecond, unit: str) -> str:
    seconds = DISTANCE_UNITS[unit] / speed
    return format_seconds(seconds)


def format_seconds(seconds: Seconds) -> str:
    sec = round(seconds)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)

    if h:
        return f"{h}:{m:02}:{s:02}"
    else:
        return f"{m:02}:{s:02}"


def format_distance(distance: Meters, unit: str) -> str:
    n_units = distance / DISTANCE_UNITS[unit]
    return f"{n_units:.2f}"


if __name__ == "__main__":
    running()
