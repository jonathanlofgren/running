import pytest
from click.testing import CliRunner

from running import (
    Mode,
    extract_num_and_unit,
    format_distance,
    format_pace,
    format_seconds,
    identify_mode,
    parse_distance,
    parse_pace,
    parse_time,
    running,
)


# --- identify_mode ---


class TestIdentifyMode:
    def test_all_three_given(self):
        assert identify_mode("1:00", "10k", "5:00") == Mode.TOO_MUCH

    def test_time_and_pace(self):
        assert identify_mode("1:00:00", None, "5:00") == Mode.DISTANCE

    def test_distance_and_pace(self):
        assert identify_mode(None, "10k", "5:00") == Mode.TIME

    def test_distance_and_time(self):
        assert identify_mode("1:00:00", "10k", None) == Mode.PACE

    def test_only_pace(self):
        assert identify_mode(None, None, "5:00") == Mode.NOT_ENOUGH

    def test_only_distance(self):
        assert identify_mode(None, "10k", None) == Mode.NOT_ENOUGH

    def test_only_time(self):
        assert identify_mode("1:00:00", None, None) == Mode.NOT_ENOUGH

    def test_nothing(self):
        assert identify_mode(None, None, None) == Mode.NOT_ENOUGH


# --- extract_num_and_unit ---


class TestExtractNumAndUnit:
    def test_number_and_unit(self):
        assert extract_num_and_unit("10km") == (10.0, "km")

    def test_decimal(self):
        assert extract_num_and_unit("5.5miles") == (5.5, "miles")

    def test_number_only(self):
        assert extract_num_and_unit("42") == (42.0, "")

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            extract_num_and_unit("abc")


# --- parse_time ---


class TestParseTime:
    def test_colon_mmss(self):
        assert parse_time("5:30") == 5 * 60 + 30

    def test_colon_hhmmss(self):
        assert parse_time("1:30:00") == 1 * 3600 + 30 * 60

    def test_seconds_unit(self):
        assert parse_time("100sec") == 100

    def test_minutes_unit(self):
        assert parse_time("2min") == 120

    def test_hours_unit(self):
        assert parse_time("1h") == 3600

    def test_bare_number_defaults_seconds(self):
        assert parse_time("90") == 90

    def test_unit_name_only(self):
        assert parse_time("hour") == 3600
        assert parse_time("minute") == 60

    def test_days(self):
        assert parse_time("2days") == 2 * 86400


# --- parse_distance ---


class TestParseDistance:
    def test_marathon(self):
        assert parse_distance("marathon", "km") == 42195

    def test_half_marathon(self):
        assert parse_distance("half-marathon", "km") == 42195 / 2
        assert parse_distance("half", "km") == 42195 / 2

    def test_numeric_km(self):
        assert parse_distance("10km", "km") == 10000

    def test_numeric_miles(self):
        assert parse_distance("1mile", "km") == 1609.344

    def test_bare_number_uses_default(self):
        assert parse_distance("5", "km") == 5000
        assert parse_distance("5", "mile") == 5 * 1609.344

    def test_meters(self):
        assert parse_distance("800m", "km") == 800


# --- parse_pace ---


class TestParsePace:
    def test_pace_with_slash(self):
        # 5:00/km => 5 min per km => 1000m / 300s
        speed = parse_pace("5:00/km", "km")
        assert speed == pytest.approx(1000 / 300)

    def test_pace_with_mile_unit(self):
        # 8:00/mile => 8 min per mile
        speed = parse_pace("8:00/mile", "km")
        assert speed == pytest.approx(1609.344 / 480)

    def test_pace_without_slash_uses_default(self):
        # "5:00" with default unit km => 1000m / 300s
        speed = parse_pace("5:00", "km")
        assert speed == pytest.approx(1000 / 300)

    def test_named_pace_kipchoge(self):
        speed = parse_pace("kipchoge", "km")
        assert speed == pytest.approx(42195 / (2 * 3600 + 1 * 60 + 39))

    def test_named_pace_bolt(self):
        speed = parse_pace("bolt", "km")
        assert speed == pytest.approx(100 / 9.58)


# --- format_seconds ---


class TestFormatSeconds:
    def test_minutes_only(self):
        assert format_seconds(300) == "05:00"

    def test_hours_minutes_seconds(self):
        assert format_seconds(3661) == "1:01:01"

    def test_sub_minute(self):
        assert format_seconds(45) == "00:45"

    def test_rounding(self):
        assert format_seconds(59.6) == "01:00"


# --- format_pace ---


class TestFormatPace:
    def test_5min_per_km(self):
        speed = 1000 / 300  # 5:00/km
        assert format_pace(speed, "km") == "05:00"

    def test_4min30_per_km(self):
        speed = 1000 / 270  # 4:30/km
        assert format_pace(speed, "km") == "04:30"


# --- format_distance ---


class TestFormatDistance:
    def test_km(self):
        assert format_distance(10000, "km") == "10.00"

    def test_miles(self):
        assert format_distance(1609.344, "mile") == "1.00"

    def test_decimal(self):
        assert format_distance(5500, "km") == "5.50"


# --- CLI integration tests ---


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_pace_and_distance_gives_time(self):
        result = self.runner.invoke(running, ["--pace", "5:00", "--distance", "10km"])
        assert result.exit_code == 0
        assert "Elapsed time:" in result.output
        assert "50:00" in result.output

    def test_pace_and_time_gives_distance(self):
        result = self.runner.invoke(running, ["--pace", "5:00", "--time", "50min"])
        assert result.exit_code == 0
        assert "Travelled distance:" in result.output
        assert "10.00" in result.output

    def test_distance_and_time_gives_pace(self):
        result = self.runner.invoke(running, ["--distance", "10km", "--time", "50:00"])
        assert result.exit_code == 0
        assert "Required pace:" in result.output
        assert "05:00" in result.output

    def test_marathon_pace(self):
        result = self.runner.invoke(running, ["-p", "4:30", "-d", "marathon"])
        assert result.exit_code == 0
        assert "Elapsed time:" in result.output

    def test_mile_unit(self):
        result = self.runner.invoke(
            running, ["-p", "8:00", "-d", "10km", "-u", "mile"]
        )
        assert result.exit_code == 0
        assert "Elapsed time:" in result.output

    def test_bolt_pace(self):
        result = self.runner.invoke(running, ["-p", "bolt", "-d", "marathon"])
        assert result.exit_code == 0
        assert "1:07" in result.output

    def test_not_enough_args(self):
        result = self.runner.invoke(running, ["--pace", "5:00"])
        assert result.exit_code == 0
        assert "atleast two" in result.output

    def test_too_many_args(self):
        result = self.runner.invoke(
            running, ["--pace", "5:00", "--distance", "10km", "--time", "50:00"]
        )
        assert result.exit_code == 0
        assert "omitting one" in result.output

    def test_help(self):
        result = self.runner.invoke(running, ["--help"])
        assert result.exit_code == 0
        assert "pace" in result.output.lower()
