import pytest
from click.testing import CliRunner

from running import running

runner = CliRunner()


def run(*args):
    return runner.invoke(running, list(args))


# --- Calculate elapsed time (given pace + distance) ---

ELAPSED_TIME_CASES = [
    # (args, expected_time)
    (["-p", "5:00", "-d", "10km"], "50:00"),
    (["-p", "4:30", "-d", "marathon"], "3:09:53"),
    (["-p", "5:00/km", "-d", "10km"], "50:00"),
    (["-p", "6min/mile", "-d", "1mile"], "06:00"),
    (["-p", "bolt", "-d", "marathon"], "1:07"),
    (["-p", "kipchoge", "-d", "marathon"], "2:01:09"),
    (["-p", "5:00", "-d", "half-marathon"], "1:45"),
    (["-p", "5:00", "-d", "half"], "1:45"),
    (["-p", "8:00", "-d", "800m"], "06:24"),
]


@pytest.mark.parametrize("args, expected_time", ELAPSED_TIME_CASES)
def test_elapsed_time(args, expected_time):
    result = run(*args)
    assert result.exit_code == 0
    assert "Elapsed time:" in result.output
    assert expected_time in result.output


# --- Calculate travelled distance (given pace + time) ---

TRAVELLED_DISTANCE_CASES = [
    # (args, expected_distance)
    (["-p", "5:00", "-t", "50min"], "10.00"),
    (["-p", "5:00", "-t", "1:00:00"], "12.00"),
    (["-p", "6min/mile", "-t", "1hour"], "16.09"),
    (["-p", "5:00", "-t", "25min"], "5.00"),
    (["-p", "4:30", "-t", "2h"], "26.67"),
]


@pytest.mark.parametrize("args, expected_distance", TRAVELLED_DISTANCE_CASES)
def test_travelled_distance(args, expected_distance):
    result = run(*args)
    assert result.exit_code == 0
    assert "Travelled distance:" in result.output
    assert expected_distance in result.output


# --- Calculate required pace (given distance + time) ---

REQUIRED_PACE_CASES = [
    # (args, expected_pace)
    (["-d", "10km", "-t", "50:00"], "05:00"),
    (["-d", "marathon", "-t", "3:09:53"], "04:30"),
    (["-d", "1mile", "-t", "6min"], "03:44"),
    (["-d", "5km", "-t", "25:00"], "05:00"),
    (["-d", "half-marathon", "-t", "1:45:00"], "04:59"),
]


@pytest.mark.parametrize("args, expected_pace", REQUIRED_PACE_CASES)
def test_required_pace(args, expected_pace):
    result = run(*args)
    assert result.exit_code == 0
    assert "Required pace:" in result.output
    assert expected_pace in result.output


# --- Unit flag changes output unit ---

UNIT_FLAG_CASES = [
    (["-p", "8:00", "-d", "10km", "-u", "mile"], "Elapsed time:"),
    (["-p", "5:00", "-t", "1hour", "-u", "mile"], "Travelled distance:"),
    (["-d", "10km", "-t", "50:00", "-u", "mile"], "Required pace:"),
]


@pytest.mark.parametrize("args, expected_label", UNIT_FLAG_CASES)
def test_unit_flag(args, expected_label):
    result = run(*args)
    assert result.exit_code == 0
    assert expected_label in result.output


# --- Short flags work the same as long flags ---

SHORT_FLAG_CASES = [
    (["-p", "5:00", "-d", "10km"], ["--pace", "5:00", "--distance", "10km"]),
    (["-p", "5:00", "-t", "50min"], ["--pace", "5:00", "--time", "50min"]),
    (["-d", "10km", "-t", "50:00"], ["--distance", "10km", "--time", "50:00"]),
]


@pytest.mark.parametrize("short_args, long_args", SHORT_FLAG_CASES)
def test_short_flags_match_long_flags(short_args, long_args):
    short_result = run(*short_args)
    long_result = run(*long_args)
    assert short_result.output == long_result.output


# --- Error cases ---


def test_not_enough_args():
    result = run("--pace", "5:00")
    assert result.exit_code == 0
    assert "at least two" in result.output


def test_no_args():
    result = run()
    assert result.exit_code == 0
    assert "at least two" in result.output


def test_too_many_args():
    result = run("--pace", "5:00", "--distance", "10km", "--time", "50:00")
    assert result.exit_code == 0
    assert "omitting one" in result.output


# --- Splits ---

SPLITS_CASES = [
    # 3km at 5:00/km -> 3 even splits
    (
        ["-p", "5:00", "-d", "3km", "--splits"],
        ["1 km", "05:00", "2 km", "10:00", "3 km", "15:00"],
    ),
    # Marathon at 4:30 -> first, last full, and partial split
    (
        ["-p", "4:30", "-d", "marathon", "--splits"],
        ["1 km", "04:30", "42 km", "42.195 km"],
    ),
    # Half-marathon partial split present
    (
        ["-p", "5:00", "-d", "half-marathon", "-s"],
        ["1 km", "21 km", "21.098 km"],
    ),
]


@pytest.mark.parametrize("args, expected_fragments", SPLITS_CASES)
def test_splits(args, expected_fragments):
    result = run(*args)
    assert result.exit_code == 0
    assert "Splits:" in result.output
    for fragment in expected_fragments:
        assert fragment in result.output


def test_splits_with_mile_unit():
    result = run("-p", "8:00/mile", "-d", "3miles", "-u", "mile", "--splits")
    assert result.exit_code == 0
    assert "1 mile" in result.output
    assert "2 mile" in result.output
    assert "3 mile" in result.output


def test_splits_short_distance():
    result = run("-p", "5:00", "-d", "800m", "--splits")
    assert result.exit_code == 0
    assert "0.8 km" in result.output
    assert "1 km" not in result.output


def test_splits_exact_distance():
    result = run("-p", "5:00", "-d", "5km", "--splits")
    assert result.exit_code == 0
    assert "5 km" in result.output
    split_lines = [
        line
        for line in result.output.strip().split("\n")
        if "km" in line and line.strip()[0].isdigit()
    ]
    assert len(split_lines) == 5


def test_splits_distance_mode():
    result = run("-p", "5:00", "-t", "12min", "--splits")
    assert result.exit_code == 0
    assert "Travelled distance:" in result.output
    assert "1 km" in result.output
    assert "2 km" in result.output
    assert "2.4 km" in result.output


def test_splits_pace_mode():
    result = run("-d", "10km", "-t", "50:00", "--splits")
    assert result.exit_code == 0
    assert "Required pace:" in result.output
    assert "1 km" in result.output
    assert "10 km" in result.output


def test_splits_ignored_on_error():
    result = run("-p", "5:00", "--splits")
    assert result.exit_code == 0
    assert "at least two" in result.output


# --- Race predictions ---

PREDICT_CASES = [
    # 10K in 45:00 -> should show all race distances
    (
        ["-d", "10km", "-t", "45:00", "--predict"],
        ["Race predictions:", "1500m", "1 mile", "5K", "10K", "Half-marathon", "Marathon"],
    ),
    # Short flag -r works the same
    (
        ["-d", "10km", "-t", "45:00", "-r"],
        ["Race predictions:", "Marathon"],
    ),
]


@pytest.mark.parametrize("args, expected_fragments", PREDICT_CASES)
def test_predict(args, expected_fragments):
    result = run(*args)
    assert result.exit_code == 0
    for fragment in expected_fragments:
        assert fragment in result.output


def test_predict_pace_mode():
    result = run("-d", "5km", "-t", "25:00", "--predict")
    assert result.exit_code == 0
    assert "Required pace:" in result.output
    assert "Race predictions:" in result.output
    assert "Marathon" in result.output


def test_predict_time_mode():
    result = run("-p", "5:00", "-d", "10km", "--predict")
    assert result.exit_code == 0
    assert "Elapsed time:" in result.output
    assert "Race predictions:" in result.output


def test_predict_distance_mode():
    result = run("-p", "5:00", "-t", "50min", "--predict")
    assert result.exit_code == 0
    assert "Travelled distance:" in result.output
    assert "Race predictions:" in result.output


def test_predict_with_splits():
    result = run("-d", "10km", "-t", "45:00", "--predict", "--splits")
    assert result.exit_code == 0
    assert "Splits:" in result.output
    assert "Race predictions:" in result.output


def test_predict_ignored_on_error():
    result = run("-p", "5:00", "--predict")
    assert result.exit_code == 0
    assert "at least two" in result.output
    assert "Race predictions:" not in result.output


def test_predict_short_flag():
    short_result = run("-d", "10km", "-t", "45:00", "-r")
    long_result = run("-d", "10km", "-t", "45:00", "--predict")
    assert short_result.output == long_result.output


def test_predict_shows_pace():
    result = run("-d", "10km", "-t", "45:00", "--predict")
    assert result.exit_code == 0
    assert "/km" in result.output


def test_predict_mile_unit():
    result = run("-d", "10km", "-t", "45:00", "--predict", "-u", "mile")
    assert result.exit_code == 0
    assert "/mile" in result.output


# --- Help ---


def test_help():
    result = run("--help")
    assert result.exit_code == 0
    assert "--pace" in result.output
    assert "--distance" in result.output
    assert "--time" in result.output
    assert "--unit" in result.output
    assert "--splits" in result.output
    assert "--predict" in result.output
