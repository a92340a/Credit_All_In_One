import os
import sys
import logging
from datetime import datetime
import time 

class MyLogger(logging.Logger):
    def __init__(self, name, level=logging.INFO):
        super().__init__(name, level)
        self.logger_formatter = logging.Formatter(u'[%(asctime)s][%(levelname)s]: %(message)s [%(threadName)s]', datefmt='%Y-%m-%d %H:%M:%S')

    def console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.logger_formatter)
        self.addHandler(console_handler)

    def file_handler(self, day):
        log_path = f'log/{self.name}_{day}.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(self.logger_formatter)
        self.addHandler(file_handler)

# datetime
now = datetime.now()
today = now.strftime('%Y%m%d')
current_time = now.strftime('%H%M%S')

if __name__ == '__main__':
    test_logger = MyLogger(__name__)
    test_logger.file_handler(today)
    test_logger.info(current_time)
    test_logger.info(time.time())
