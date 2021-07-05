"""Python logger that outputs to stdout and a file."""
import logging
from logging.handlers import WatchedFileHandler, TimedRotatingFileHandler
import sys

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
DEFAULT_LOG_FILE = "/dev/null"
DEFAULT_LOG_LEVEL = logging.INFO


class Log:  # pylint: disable=R0903
    """Logger that logs to stdout and a file."""
    @classmethod
    def _get_console_handler(cls):
        """Init and return console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

    @classmethod
    def _get_file_handler(cls, log_file, timed_file_handler=False):
        """Init and return stdout handler."""
        if timed_file_handler:
            file_handler = TimedRotatingFileHandler(log_file, when='midnight')
        else:
            file_handler = WatchedFileHandler(log_file)
        file_handler.setFormatter(FORMATTER)
        return file_handler

    @classmethod
    def get_logger(cls, logger_name, log_level=DEFAULT_LOG_LEVEL, log_file=DEFAULT_LOG_FILE):
        """Get a logger instance."""
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        if not logger.hasHandlers():  # avoid adding the same handlers more than once
            logger.addHandler(cls._get_console_handler())
            logger.addHandler(cls._get_file_handler(log_file))

        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False

        return logger
