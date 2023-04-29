import os
import time
import re
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import send_sms
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.events import EventFiringWebDriver
from utils.logger import EventListener

JOB_LIST = []
LANGUAGES = []


@pytest.fixture(autouse=True)
def setup():
    global driver
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    breakpoint()
    driver = EventFiringWebDriver(webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options),
                                  EventListener())
    driver.implicitly_wait(4)
    driver.get('https://www.google.com')
    yield
    driver.quit()


# Search terms to remember (100+ entries in general roles) - check for python when searching
# senior automation tester remote jobs
# software development engineer in test remote jobs
@pytest.fixture(params=['senior automation tester remote jobs', 'senior automation tester remote jobs'])
def job_search_terms(request):
    return request.param


def get_all_google_job_listing_names(job_count):
    if isinstance(job_count, int):
        while True:
            job_listings = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
            driver.execute_script('arguments[0].scrollIntoView();', job_listings[-1])
            job_listings2 = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
            if len(job_listings2) >= job_count - 4:
                driver.execute_script('arguments[0].scrollIntoView();', job_listings[0])
                return job_listings2
    else:
        job_listings = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
        return job_listings


def open_google_job_listings(job_search):
    driver.find_element(By.XPATH, '//div[text()="Reject all"]').click()
    search_field = driver.find_element(By.NAME, 'q')
    search_field.send_keys(job_search)
    # Sleep added since sending keys quickly adds a line break in the google search field
    time.sleep(0.5)
    search_field.send_keys(Keys.ENTER)

    job_count_link = driver.find_element(By.XPATH,
                                         '//span[contains(text(),"more jobs") or contains(text(), "Explore jobs")]/ancestor::a[@href]')
    job_count = re.sub('[^0-9]', '', job_count_link.text)
    job_count_link.click()

    if job_count == '':
        return

    return int(job_count)


def expand_full_descriptions(job_title):
    all_descriptions_buttons = driver.find_elements(By.XPATH,
                                                    f'//div[text()="{job_title.text}"]/ancestor::div[@class]/descendant::g-inline-expansion-bar[@role="button"]')

    driver.execute_script('arguments[0].scrollIntoView();', all_descriptions_buttons[-1])
    driver.execute_script('arguments[0].click();', all_descriptions_buttons[-1])


def get_job_posting_link(job_title):
    job_link_buttons = driver.find_elements(By.XPATH,
                                            '//div[@class="whazf bD1FPe"]/descendant::div[@class="iSJ1kb va9cAf"]')
    job_link_hrefs = driver.find_elements(By.XPATH,
                                          '//div[@class="whazf bD1FPe"]/descendant::div[@class="iSJ1kb va9cAf"]/ancestor::a["href"]')

    full_description = driver.find_elements(By.CLASS_NAME, 'HBvzbc')

    for web_element_buttons in full_description:
        if web_element_buttons.text == '':
            full_description.remove(web_element_buttons)

    for description in full_description:
        if all(word in description.text.lower() for word in ['python']):
            for button, href in zip(job_link_buttons, job_link_hrefs):
                if 'linkedin' in button.text.lower():
                    continue
                else:
                    job_posting_url = href.get_attribute('href')
                    # send_sms.send_sms(f'{job_title.text} - {job_posting_url}')
                    JOB_LIST.append(job_title)
                    print(f'{len(JOB_LIST)}: {job_title.text} - {job_posting_url}')

                break


def test_google_search(job_search_terms):
    # TODO 1. Put on github when done

    # Search term entered for google search
    job_count = open_google_job_listings(job_search_terms)
    job_listings = get_all_google_job_listing_names(job_count)

    for job_title in job_listings:
        if 'junior' in job_title.text.lower():
            continue

        elif any(word in job_title.text.lower() for word in ['qa', 'test', 'automation', 'python']):
            driver.execute_script('arguments[0].scrollIntoView();', job_title)
            driver.execute_script('arguments[0].click();', job_title)
            expand_full_descriptions(job_title)
            get_job_posting_link(job_title)

    print(f'{len(JOB_LIST)} jobs found')

