from loguru import logger
import os

logger.remove()
class MyLogger:
    def __init__(self, filename):
        self.filename = filename
        self.logger = logger
        self.filepath = f"logs/{filename}.log"
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        logger.add(self.filepath, enqueue=True, level="INFO",colorize=True, rotation="00:00", retention=1, backtrace=True, diagnose=True, format="{time:YYYY-MM-DD HH:mm:ss.SSS zz} | {level} | {file} | {message}")