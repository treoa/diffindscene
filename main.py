import os

from pathlib import Path

from src.utils.logger import CustomLogger

log = CustomLogger()

a: int = 12

log.print(level="debug", message=f"This is the debug message and the test str is {a}")