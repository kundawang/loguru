import sys
import json
from unittest.mock import MagicMock

import pytest

from loguru import logger

from .conftest import parse

if sys.version_info >= (3, 14):
    from string.templatelib import Interpolation, Template


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string(writer):
    logger.add(writer, format="{message}", colorize=False)

    # We can't just use t"2**8 = {2**8}", because its a syntax error before python-3.14.
    logger.info(Template("2**8 = ", Interpolation(2**8)))

    result = writer.read()
    assert result == "2**8 = 256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_is_lazy(writer):
    logger.add(writer, level="INFO", format="{message}", colorize=False)

    debug_tracker = MagicMock()
    debug_tracker.__str__.return_value = "xxx"

    info_tracker = MagicMock()
    info_tracker.__str__.return_value = "xxx"

    logger.debug(Template("debug = ", Interpolation(debug_tracker)))
    logger.info(Template("info = ", Interpolation(info_tracker)))

    result = writer.read()
    assert len(result.strip().split("\n")) == 1
    assert result == "info = xxx\n"
    assert not debug_tracker.__str__.called
    assert info_tracker.__str__.called


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_conversion_spec(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template("2**8 = ", Interpolation("2**8", "2**8", "r")))

    result = writer.read()
    assert result == "2**8 = '2**8'\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_format_spec(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template("2**8 = ", Interpolation(2**8, "2**8", None, ".2f")))

    result = writer.read()
    assert result == "2**8 = 256.00\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_two_consecutive_interpolations(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template("2**8 = ", Interpolation(5 * 5), Interpolation(2 * 3)))

    result = writer.read()
    assert result == "2**8 = 256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_two_consecutive_strings(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template("2**8", " = ", Interpolation(2**8)))

    result = writer.read()
    assert result == "2**8 = 256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_without_string(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template(Interpolation(2**8)))

    result = writer.read()
    assert result == "256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_without_interpolation(writer):
    logger.add(writer, format="{message}", colorize=False)

    logger.info(Template("256"))

    result = writer.read()
    assert result == "256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_nested(writer):
    inner = Template(Interpolation(2**8))
    template = Template("2**8 = ", Interpolation(inner))

    logger.add(writer, format="{message}", colorize=False)

    logger.info(template)

    result = writer.read()
    assert result == "2**8 = 256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_colors(writer):
    logger.add(writer, format="{message}", colorize=True)

    logger.opt(colors=True).info(Template("<red>2**8 = ", Interpolation(2**8), "</red>"))

    result = writer.read()
    assert result == parse("<red>2**8 = 256</red>\n")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_colors_and_args(writer):
    logger.add(writer, format="{message}", colorize=True)

    logger.opt(colors=True).info(
        Template("<red>{calc} = ", Interpolation(2**8), "</red>"),
        calc="2**8",
    )

    result = writer.read()
    assert result == parse("<red>2**8 = 256</red>\n")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_raw(writer):
    logger.add(writer, format="{time} {message}", colorize=True)

    logger.opt(raw=True).info(Template("2**8 = ", Interpolation(2**8)))

    result = writer.read()
    assert result == parse("2**8 = 256")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_raw_and_args(writer):
    logger.add(writer, format="{time} {message}", colorize=True)

    logger.opt(raw=True).info(
        Template("{calc} = ", Interpolation(2**8)),
        calc="2**8",
    )

    result = writer.read()
    assert result == parse("2**8 = 256")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_raw_and_colors(writer):
    logger.add(writer, format="{time} {message}", colorize=True)

    logger.opt(raw=True, colors=True).info(Template("<red>2**8 = ", Interpolation(2**8), "</red>"))

    result = writer.read()
    assert result == parse("<red>2**8 = 256</red>")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_raw_and_colors_and_args(writer):
    logger.add(writer, format="{time} {message}", colorize=True)

    logger.opt(raw=True, colors=True).info(
        Template("<red>{calc} = ", Interpolation(2**8), "</red>"),
        calc="2**8",
    )

    result = writer.read()
    assert result == parse("<red>2**8 = 256</red>")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_with_interpolated_colors(writer):
    logger.add(writer, format="{message}", colorize=True)

    logger.opt(colors=True).info(
        Template(Interpolation("<red>"), "2**8 = 256", Interpolation("</red>"))
    )

    result = writer.read()
    assert result == parse("<red>2**8 = 256</red>\n")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_in_catch_message(writer):
    logger.add(writer, format=lambda _: "{level}: {message}\n", colorize=False)

    with logger.catch(message=Template("2**8 = ", Interpolation(2**8))):
        raise ValueError("An error occurred")

    result = writer.read()
    assert result == "ERROR: 2**8 = 256\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_adds_interpolations_to_extra(writer):
    logger.add(writer, format="{message} | {extra}", colorize=False)

    logger.info(Template("2**8 = ", Interpolation(2**8, "2**8")))

    result = writer.read()
    assert result == "2**8 = 256 | {'2**8': 256}\n"


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_extra_stores_raw_value():
    extra = None

    def sink(message):
        nonlocal extra
        extra = message.record["extra"]

    logger.add(sink, format="{message}", colorize=False)

    logger.info(Template("value = ", Interpolation(3.14159, "pi", None, ".2f")))

    assert extra == {"pi": 3.14159}


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_extra_with_nested_template():
    extra = None

    def sink(message):
        nonlocal extra
        extra = message.record["extra"]

    logger.add(sink, format="{message}", colorize=False)

    inner = Template(Interpolation(2**8, "2**8"))
    logger.info(Template("2**8 = ", Interpolation(inner, "inner")))

    assert extra == {"2**8": 256}


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_extra_without_expression():
    extra = None

    def sink(message):
        nonlocal extra
        extra = message.record["extra"]

    logger.add(sink, format="{message}", colorize=False)

    logger.info(Template("2**8 = ", Interpolation(2**8)))

    assert extra == {}


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_extra_merged_with_bound_extra():
    extra = None

    def sink(message):
        nonlocal extra
        extra = message.record["extra"]

    logger.add(sink, format="{message}", colorize=False)

    logger.bind(user="alice", ip="192.168.0.1").info(
        Template("User ", Interpolation("alice", "user"), " logged in")
    )

    assert extra == {"user": "alice", "ip": "192.168.0.1"}


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Template Strings not supported")
def test_template_string_extra_serialized(writer):
    logger.add(writer, format="{message}", serialize=True)

    logger.info(Template("2**8 = ", Interpolation(2**8, "2**8")))

    record = json.loads(writer.read())["record"]
    assert record["message"] == "2**8 = 256"
    assert record["extra"] == {"2**8": 256}
