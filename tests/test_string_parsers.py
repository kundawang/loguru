import datetime

import pytest

from loguru._string_parsers import parse_time


@pytest.mark.parametrize(
    ("time_str", "expected"),
    [
        ("13", datetime.time(13)),
        ("13:00", datetime.time(13, 0)),
        ("13:00:00", datetime.time(13, 0, 0)),
        ("13:00:00.123456", datetime.time(13, 0, 0, 123456)),
        ("11am", datetime.time(11)),
        ("11pm", datetime.time(23)),
        ("11 AM", datetime.time(11)),
        ("11 PM", datetime.time(23)),
        ("1am", datetime.time(1)),
        ("1pm", datetime.time(13)),
        ("12am", datetime.time(0)),
        ("12pm", datetime.time(12)),
        ("12 AM", datetime.time(0)),
        ("12 PM", datetime.time(12)),
        ("1:30am", datetime.time(1, 30)),
        ("1:30pm", datetime.time(13, 30)),
        ("1:30 AM", datetime.time(1, 30)),
        ("1:30 PM", datetime.time(13, 30)),
        ("11:59pm", datetime.time(23, 59)),
        ("12:00am", datetime.time(0, 0)),
        ("12:00pm", datetime.time(12, 0)),
        ("12:30am", datetime.time(0, 30)),
        ("12:30pm", datetime.time(12, 30)),
        ("1:30:45pm", datetime.time(13, 30, 45)),
        ("1:30:45.123pm", datetime.time(13, 30, 45, 123000)),
        ("1:30:45 PM", datetime.time(13, 30, 45)),
        ("1:0:0.0 pm", datetime.time(13, 0, 0)),
    ],
)
def test_parse_time_valid(time_str, expected):
    assert parse_time(time_str) == expected


@pytest.mark.parametrize(
    "time_str",
    [
        "13pm",
        "0am",
        "25",
        "1:60pm",
        "1:30:45:12",
    ],
)
def test_parse_time_invalid(time_str):
    with pytest.raises(ValueError, match="Unrecognized format while parsing time"):
        parse_time(time_str)


@pytest.mark.parametrize("time_str", ["", "noon", "abc", "am", "pm", "1 pm 30"])
def test_parse_time_not_a_time(time_str):
    assert parse_time(time_str) is None
