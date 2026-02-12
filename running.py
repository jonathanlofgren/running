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
PACES = {
    "kipchoge": 42195 / (2 * HOUR + 1 * MINUTE + 9),
    "kiptum": 42195 / (2 * HOUR + 0 * MINUTE + 35),
    "bolt": 100 / 9.58,
}
RIEGEL_EXPONENT = 1.06
RACE_DISTANCES: list[tuple[str, float]] = [
    ("1500m", 1500),
    ("1 mile", 1609.344),
    ("5K", 5000),
    ("10K", 10000),
    ("Half-marathon", 42195 / 2),
    ("Marathon", 42195),
]


class Mode(enum.Enum):
    PACE = enum.auto()
    DISTANCE = enum.auto()
    TIME = enum.auto()
    NOT_ENOUGH = enum.auto()
    TOO_MUCH = enum.auto()


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
@click.option(
    "--splits",
    "-s",
    is_flag=True,
    default=False,
    help="Show split times at each unit interval.",
)
@click.option(
    "--predict",
    "-r",
    is_flag=True,
    default=False,
    help="Show predicted race times using the Riegel formula.",
)
def running(time: str, distance: str, pace: str, unit: str, splits: bool, predict: bool) -> None:
    mode = identify_mode(time, distance, pace)
    meters: Meters | None = None
    speed: MetersPerSecond | None = None

    if mode == Mode.PACE:
        seconds = parse_time(time)
        meters = parse_distance(distance, unit)
        speed = meters / seconds
        output_line("Required pace:", format_pace(speed, unit), "/" + unit)

    elif mode == Mode.DISTANCE:
        speed = parse_pace(pace, unit)
        seconds = parse_time(time)
        meters = speed * seconds
        output_line("Travelled distance:", format_distance(meters, unit), unit)

    elif mode == Mode.TIME:
        speed = parse_pace(pace, unit)
        meters = parse_distance(distance, unit)
        seconds = meters / speed
        output_line("Elapsed time:", format_seconds(seconds), "[H:]MM:SS")

    elif mode == Mode.NOT_ENOUGH:
        error("You need to give at least two of time, distance or pace.")

    elif mode == Mode.TOO_MUCH:
        error("You provided time, distance and pace. Try omitting one.")

    if meters is not None and speed is not None:
        if splits:
            print_splits(meters, speed, unit)
        if predict:
            print_predictions(meters, speed, unit)


def output_line(pre: str, bolded: str, post: str) -> None:
    click.secho(f"{pre} ", dim=True, nl=False)
    click.secho(bolded, bold=True, nl=False)
    click.secho(f" {post}", dim=True)


def error(message: str) -> None:
    click.secho(message, fg="red")
    click.echo("See running --help for further instructions.")


def identify_mode(time: str | None, distance: str | None, pace: str | None) -> Mode:
    def given(*metrics: str | None) -> bool:
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


def extract_num_and_unit(num_and_unit: str) -> tuple[float, str]:
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


def _format_split_label(distance_units: float) -> str:
    if distance_units == int(distance_units):
        return str(int(distance_units))
    return f"{distance_units:.3f}".rstrip("0").rstrip(".")


def print_splits(meters: Meters, speed: MetersPerSecond, unit: str) -> None:
    interval = DISTANCE_UNITS[unit]
    total_units = meters / interval
    full_intervals = int(total_units)

    lines: list[tuple[str, str]] = []
    for i in range(1, full_intervals + 1):
        cumulative_seconds = (i * interval) / speed
        lines.append((str(i), format_seconds(cumulative_seconds)))

    remainder = total_units - full_intervals
    if remainder > 1e-9:
        label = _format_split_label(total_units)
        lines.append((label, format_seconds(meters / speed)))

    if not lines:
        return

    max_label_width = max(len(label) for label, _ in lines)

    click.echo()
    click.secho("Splits:", bold=True)
    for label, time_str in lines:
        click.secho(f"  {label:>{max_label_width}} {unit}  ", dim=True, nl=False)
        click.echo(time_str)


def print_predictions(meters: Meters, speed: MetersPerSecond, unit: str) -> None:
    seconds = meters / speed

    lines: list[tuple[str, str, str]] = []
    for name, race_meters in RACE_DISTANCES:
        predicted = seconds * (race_meters / meters) ** RIEGEL_EXPONENT
        pace_str = format_pace(race_meters / predicted, unit)
        lines.append((name, format_seconds(predicted), pace_str))

    max_label_width = max(len(name) for name, _, _ in lines)
    max_time_width = max(len(time_str) for _, time_str, _ in lines)

    click.echo()
    click.secho("Race predictions:", bold=True)
    for name, time_str, pace_str in lines:
        click.secho(f"  {name:>{max_label_width}}  ", dim=True, nl=False)
        click.echo(f"{time_str:>{max_time_width}}", nl=False)
        click.secho(f"   ({pace_str} /{unit})", dim=True)


if __name__ == "__main__":
    running()
