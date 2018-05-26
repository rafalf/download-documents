# -*- coding: utf-8 -*-

from selenium import webdriver
from sys import platform
from contextlib import contextmanager
import logging
import logging.config
import yaml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os
import sys
from shutil import copyfile

LOGGING_CONFIG = {
    'formatters': {
        'brief': {
            'format': '[%(asctime)s][%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'brief',
            'filename': 'log.log',
            'maxBytes': 1024*1024,
            'backupCount': 3,
        },
    },
    'loggers': {
        'main': {
            'propagate': False,
            'handlers': ['console', 'file'],
            'level': 'INFO'
        }
    },
    'version': 1
}
SITE_URL = "https://carmodyinc.com"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOWN_PATH = os.path.join(BASE_DIR, 'download')
RESULTS_PATH = os.path.join(BASE_DIR, 'results')
OUTPUT_CSV = os.path.join(BASE_DIR, "output.csv")
INPUT_CSV = os.path.join(BASE_DIR, "input.csv")


@contextmanager
def get_driver(headless=None):

    chromeOptions = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": DOWN_PATH,
        "credentials_enable_service": False,
        "password_manager_enabled": False
    }
    chromeOptions.add_experimental_option("prefs", prefs)

    chromeOptions.add_argument("--disable-extensions")
    chromeOptions.add_argument("--disable-infobars")
    if headless:
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-gpu")
    if platform == 'darwin':
        driver = webdriver.Chrome(chrome_options=chromeOptions)
    elif platform == 'linux' or platform == 'linux2':
        driver = webdriver.Chrome(chrome_options=chromeOptions)
    else:  # windows
        driver = webdriver.Chrome(os.path.join(BASE_DIR, "drivers", "chromedriver.exe"),
                                  chrome_options=chromeOptions)

    driver.get(SITE_URL)

    driver.maximize_window()
    yield driver
    #  teardown
    driver.quit()


def get_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger('main')
    log.setLevel(level=logging.getLevelName('INFO'))
    return log


def get_config():
    with open('config.yaml', 'r') as yaml_file:
        yaml_config = yaml.load(yaml_file)
        return yaml_config


def get_input():
    pass


def click_if_clickable(driver, element, logger):

    for _ in range(3):
        try:
            if element.is_enabled() and element.is_displayed():
                element.click()
                return
            else:
                logger.info('click_if_clickable not yet')
                time.sleep(1)
        except (StaleElementReferenceException, WebDriverException) as err:
            logger.warning("(StaleElementReferenceException, WebDriverException) click_if_clickable failed to click")
            time.sleep(1)
    else:
        logger.error('click_if_clickable: failed')

def click_by_css(driver, selector, logger, time_out=30):
    for _ in range(3):
        try:
            el = WebDriverWait(driver, time_out).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)),
                                                        'click_by_css: timed out on: %s' % selector)
            el.click()
            return
        except Exception as e:
            logger.warning('click_by_css: failed to click: %s', e)
            time.sleep(1)
    logger.error('click_by_css: failed')


def click_by_xpath(driver, selector, logger, time_out=30):
    for _ in range(3):
        try:
            el = WebDriverWait(driver, time_out).until(EC.element_to_be_clickable((By.XPATH, selector)),
                                                       'timed out on: %s' % selector)
            el.click()
            return
        except Exception as e:
            logger.warning('click_by_xpath: failed to click: %s', e)
            time.sleep(1)
    logger.error('click_by_xpath: failed')


def send_by_css(driver, selector, value, logger):
    for _ in range(3):
        try:
            el = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
                                                 'timed out on: %s' % selector)
            el.clear()
            el.send_keys(value)
            logger.info('send_by_css: sent: %s', value)
            return
        except Exception as e:
            logger.warning('send_by_css: failed: %s', e)
            time.sleep(1)
    logger.error('send_by_css: failed')


def get_element_by_css(driver, selector, time_out=30):
    return WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
                                                 'timed out on: %s' % selector)


def is_element_by_css(driver, selector, time_out=1):
    try:
        return WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
                                                     'timed out on: %s' % selector)
    except Exception:
        return None


def is_element_by_xpath(driver, selector, time_out=1):
    try:
        return WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, selector)),
                                                     'timed out on: %s' % selector)
    except Exception:
        return None


def get_all_elements_by_css(driver, selector, logger):
    try:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)),
            'timed out on: %s' % selector)
    except Exception as e:
        logger.error("err: %s", e)


def trk_nmbr():
    df = pd.read_csv(INPUT_CSV, converters={'TrkNbr': lambda x: str(x)})
    idles = df.loc[df['Status'] == 'idle']
    return idles.values.tolist()


def set_processed(doc_id, status="processed"):
    df = pd.read_csv(INPUT_CSV, converters={'TrkNbr': lambda x: str(x)})
    print("[INFO] setting {} processed".format(doc_id))
    df.loc[df['TrkNbr'] == doc_id, 'Status'] = status
    df.to_csv(INPUT_CSV, index=False)


def create_folder(folder_name):
    directory = os.path.join(DOWN_PATH, folder_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def append_result(dt, dn, fn, logger):
    existing_df = pd.read_csv(OUTPUT_CSV, converters={'FolderName': lambda x: str(x)})
    append_df = pd.DataFrame([[dt, dn, fn]], columns=["DocType", "DocName", "FolderName"])
    result = pd.concat([existing_df, append_df], ignore_index=True)
    logger.info(result.tail(5))
    result.to_csv(OUTPUT_CSV, index=False)


def clean_up_download(logger):

    for _ in range(60):
        af = os.listdir(DOWN_PATH)
        af.remove(".gitkeep")
        for f in af:
            os.remove(os.path.join(DOWN_PATH, f))
            logger.info('deleted: %s', f)


def move_file(source, dest, logger):

    # let it kick in
    time.sleep(0.2)

    logger.info('checking downloaded file')
    for _ in range(60):
        af = os.listdir(source)
        af.remove(".gitkeep")

        if len(af) == 1:
            if not af[0].count("crdownload") and not af[0].count(".tmp"):
                logger.info("download completed: %s", af[0])
                break
            else:
                logger.info("being downloaded: %s", af[0])
                time.sleep(1)
        else:
            logger.error("incorrect number of files found: %s", len(af))
            clean_up_download(logger)
            return
    else:
        logger.error("failed to download, listdir: %s", os.listdir(source))
        clean_up_download(logger)
        return

    try:
        copyfile(os.path.join(source, af[0]), os.path.join(dest, af[0]))
        logger.info('copied as: {}'.format(os.path.join(dest, af[0])))

        if not os.path.exists(os.path.join(dest, af[0])):
            logger.error("os.path.exists failed on: %s", os.path.join(dest, af[0]))
            input("please enter and any key and press ENTER to continue ... ")

        os.remove(os.path.join(source, af[0]))
        logger.info('deleted: {}'.format(os.path.join(source, af[0])))
        return af[0]
    except:
        logger.error("failed to copy|delete: {}".format(af[0]))


def download():

    conf = get_config()
    nmbrs = trk_nmbr()
    logger = get_logger()
    fn = None

    clean_up_download(logger)

    logger.info("found idle numbers (total: %s): to process %s", len(nmbrs), nmbrs)

    with get_driver() as driver:

        # login
        send_by_css(driver, "#txtUN", conf.get("user"), logger)
        send_by_css(driver, "#txtPW", conf.get("password"), logger)
        click_by_css(driver, "[name=\"BtnLogin\"]", logger)

        get_element_by_css(driver, "#mMain_1")

        logger.info("logged in.")

        # search
        click_by_xpath(driver, '//div[contains(text(),"Search/Add Property")]', logger)

        get_element_by_css(driver, "#txtSearch_By")
        search_url = driver.current_url

        # process collected
        for item in nmbrs:

            send_by_css(driver, "#txtSearch_By", item[0], logger)
            click_by_css(driver, '[name="BtnSubmit2"]', logger)
            logger.info("search: %s", item[0])

            if is_element_by_xpath(driver, '//td[contains(text(),"No Matching Records Found!")]'):
                logger.info("no matching records found: %s", item[0])
            else:

                docs = get_all_elements_by_css(driver, '[href*="/Docs/DocList"]', logger)
                hrefs = []
                for doc in docs:
                    href = doc.get_attribute("href")
                    hrefs.append(href)
                logger.info("collected hrefs (%s): %s", len(hrefs), hrefs)

                for href in hrefs:
                    logger.info("open: %s", href)
                    driver.get(href)

                    no_available = '//div[contains(text(),"No documents are available for the selected property!")]'
                    if is_element_by_xpath(driver, no_available):
                        logger.info("no documents are available for the selected property!")
                    else:

                        view_docs = get_all_elements_by_css(driver, '[name="BtnView"]', logger)
                        doc_types = get_all_elements_by_css(driver, 'table tr>.dataC:nth-of-type(1)', logger)

                        logger.info("documents %s found", len(view_docs))

                        folder_idx = os.path.join(RESULTS_PATH, item[0])
                        if not os.path.isdir(folder_idx):
                            os.makedirs(folder_idx)
                            logger.info("created folder: {}".format(folder_idx))

                        for view, doc_type in zip(view_docs, doc_types):
                            click_if_clickable(driver, view, logger)

                            fn = move_file(DOWN_PATH, folder_idx, logger)

                            # break this page
                            if not fn:
                                break

                            append_result(doc_type.text.strip(), fn, item[0], logger)

                        # break this item (number)
                        if not fn:
                            break

            logger.info("processed: %s with result: %s", item[0], fn)

            if fn:
                set_processed(item[0])
            else:
                set_processed(item[0], "error")

            driver.get(search_url)


if __name__ == "__main__":
    download()
