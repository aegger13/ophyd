import io
import logging
import logging.handlers

import pytest

import ophyd.log as log
from ophyd.ophydobj import OphydObject
from ophyd.status import Status


def test_validate_level():
    log.validate_level("CRITICAL")
    log.validate_level("ERROR")
    log.validate_level("WARNING")
    log.validate_level("INFO")
    log.validate_level("DEBUG")
    log.validate_level("NOTSET")

    with pytest.raises(ValueError):
        log.validate_level("TRACE")


def test_default_config_ophyd_logging():
    log.config_ophyd_logging()

    assert isinstance(log.current_handler, logging.StreamHandler)
    assert log.logger.getEffectiveLevel() <= logging.INFO
    assert log.control_layer_logger.getEffectiveLevel() <= logging.INFO


def test_config_ophyd_logging():
    datefmt = "%Y:%m:%d %H-%M-%S"
    backupCount = 10

    log.config_ophyd_logging(
        file="ophyd.log",
        datefmt=datefmt,
        color=False,
        level="DEBUG",
        backupCount=backupCount,
    )

    assert isinstance(log.current_handler, logging.handlers.TimedRotatingFileHandler)
    assert log.current_handler.backupCount == backupCount
    assert log.current_handler.formatter.datefmt == datefmt
    assert log.logger.getEffectiveLevel() <= logging.DEBUG
    assert log.control_layer_logger.getEffectiveLevel() <= logging.DEBUG


def test_logger_adapter_ophyd_object():
    log_buffer = io.StringIO()
    log_stream = logging.StreamHandler(stream=log_buffer)
    log_stream.setFormatter(log.LogFormatter())

    log.logger.addHandler(log_stream)

    ophyd_object = OphydObject(name="testing")
    ophyd_object.log.info("here is some info")
    assert log_buffer.getvalue().endswith("[testing] here is some info\n")


def test_logger_adapter_status():
    log_buffer = io.StringIO()
    log_stream = logging.StreamHandler(stream=log_buffer)
    log_stream.setFormatter(log.LogFormatter())

    log.logger.addHandler(log_stream)

    status = Status()
    status.log.info("here is some info")
    assert log_buffer.getvalue().endswith(f"[{str(status)}] here is some info\n")

    status._finished(success=True)
    status.log.info("here is more info")
    assert log_buffer.getvalue().endswith(f"[{str(status)}] here is more info\n")
