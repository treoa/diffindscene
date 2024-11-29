import os
import logging
import warnings

warnings.filterwarnings("ignore")

# Custom formatter for coloring error messages red
class CustomFormatter(logging.Formatter):
    """
        A custom log formatter that adds color to log messages based on their log level.

        Args:
            fmt (str): The log message format string.

        Methods:
            format(record): Formats the log record and adds color based on the log level.

        Attributes:
            RED (str): The ANSI escape code for red color.
            RESET (str): The ANSI escape code to reset the color.
            GREEN (str): The ANSI escape code for green color.
            YELLOW (str): The ANSI escape code for yellow color.
            FORMAT (str): The default log message format string.
    """
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    # FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    

    def __init__(self, fmt=FORMAT):
        super().__init__(fmt)

    def format(self, record):
        if record.levelno == logging.ERROR:
            return f"{self.RED}{super().format(record)}{self.RESET}"
        elif record.levelno == logging.DEBUG:
            return f"{self.YELLOW}{super().format(record)}{self.RESET}"
        return super().format(record)


# Set up the logging with the custom formatter
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def logme(message, level='info'):
    """Logging message as info or error with different formatting

    Args:
        message (_type_): Message to be displayed
        level (str, optional): [error, debug, info]. Defaults to 'info'.
    """
    log_function = getattr(logger, level.lower(), logger.info)
    log_function(message)