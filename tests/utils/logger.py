from selenium.webdriver.support.events import AbstractEventListener
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

try:
    os.remove('report.log')
except FileNotFoundError as e:
    print(f'File not created {e}')

f_handler = logging.FileHandler('report.log')
formatter = logging.Formatter('%(asctime)s  -  %(levelname)s  - %(message)s')

f_handler.setFormatter(formatter)
logger.addHandler(f_handler)

class EventListener(AbstractEventListener):
    logger = logger

    def before_click(self, element, driver):
        logger.info(f'before clicking {element}' )

    def after_click(self, element, driver):
        logger.info(f'after clicking {element}' )

    def before_find(self, by, value, driver):
        logger.info(f'looking for {value} by {by}' )

    def after_find(self, by, value, driver):
        logger.info(f'found {value} by {by}' )

    def before_quit(self, driver):
        logger.info('before closing driver')


