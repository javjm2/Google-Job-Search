import time
import re
import pytest
import selenium.common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.events import EventFiringWebDriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from utils.logger import EventListener

JOB_LIST = []

# Search terms in general
SDET = 'software+development+engineer+in+test+jobs'
SENIOR_AUTOMATION_TESTER = 'senior+automation+tester+jobs'
SENIOR_TEST_AUTOMATION_ENGINEER = 'senior+test+automation+engineer+jobs'
AUTOMATION_TESTER = 'automation+tester+jobs'
TESTER_AUTOMATION_ENGINEER = 'test+automation_engineer+jobs'
QA_AUTOMATION_ENGINEER = 'qa+automation_engineer+jobs'
LEAD_QA_AUTOMATION_ENGINEER = 'lead+qa+automation_engineer+jobs'
LEAD_AUTOMATION_ENGINEER = 'lead+automation_engineer+jobs'
SENIOR_QA_ENGINEER = 'senior+qa+engineer+jobs'
QA_ENGINEER = 'qa+engineer+jobs'
QA_DATA_TEST_ENGINEER = 'qa+data_test+engineer'


# Remote first job search terms
REMOTE_TEST_AUTOMATION_ENGINEER = 'test+automation_engineer+remote+first+jobs'
REMOTE_SENIOR_QA_ENGINEER = 'senior+qa+engineer+remote+first+jobs'
REMOTE_SDET = 'software+development+engineer+in+test+remote+first+jobs'

# Contract Jobs
AUTOMATION_TESTER_CONTRACT = 'automation+tester+contract'
TEST_AUTOMATION_ENGINEER_CONTRACT = 'test+automation_engineer+contract+jobs'
SDET_CONTRACT = 'software+development+engineer+in+test+contract+jobs'
SENIOR_QA_ENGINEER_CONTRACT = 'senior+qa engineer+contract+jobs'
QA_ENGINEER_CONTRACT = 'qa+engineer+contract+jobs'
TEST_ENGINEER_CONTRACT = 'test+engineer+contract+jobs'
SYSTEM_TESTER_CONTRACT = 'system_tester_contract_jobs'

# Search terms for job description
SEARCH_TERMS = ['python']
# avoid_terms = []
AVOID_TERMS = ['on-site', 'onsite', 'offices', 'office', 'hybrid']


@pytest.fixture(params=[REMOTE_TEST_AUTOMATION_ENGINEER, REMOTE_SENIOR_QA_ENGINEER, REMOTE_SDET])
def job_search_terms(request):
    return request.param


@pytest.fixture(autouse=True)
def setup(job_search_terms):
    global driver
    driver = EventFiringWebDriver(webdriver.Edge(EdgeChromiumDriverManager().install()),
                                  EventListener())
    driver.maximize_window()
    driver.implicitly_wait(4)
    driver.get(f'https://www.google.com/search?q={job_search_terms}')
    yield
    driver.quit()


def get_all_google_job_listing_names(job_count):
    # Scroll through list of jobs on google for jobs
    if isinstance(job_count, int):
        while True:
            job_listings = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
            driver.execute_script('arguments[0].scrollIntoView();', job_listings[-1])
            time.sleep(1)
            job_listings2 = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
            if len(job_listings) == len(job_listings2):
                return job_listings2
    else:
        job_listings = driver.find_elements(By.XPATH, '//div[@class="BjJfJf PUpOsf"]')
        return job_listings


def open_google_job_listings():
    # Go to google for jobs and get number of jobs found
    try:
        driver.find_element(By.XPATH, '//div[text()="Reject all"]').click()
    except selenium.common.NoSuchElementException:
        pass

    job_count_link = driver.find_element(By.XPATH,
                                         '//span[contains(text(),"more jobs") or contains(text(), "Explore jobs")]/ancestor::a[@href]')
    job_count = re.sub('[^0-9]', '', job_count_link.text)
    job_count_link.click()

    if job_count == '':
        return

    return int(job_count)


def expand_full_descriptions():
    # Open full job descriptions
    all_descriptions_buttons = driver.find_elements(By.XPATH, '//*[contains(text(), "Show full description")]')

    driver.execute_script('arguments[0].scrollIntoView();', all_descriptions_buttons[-1])
    driver.execute_script('arguments[0].click();', all_descriptions_buttons[-1])


def get_job_posting_link(job_title):
    # Get link to relevant job postings
    job_link_buttons = driver.find_elements(By.XPATH,
                                            '//div[@class="whazf bD1FPe"]/descendant::div[@class="iSJ1kb va9cAf"]')
    job_link_hrefs = driver.find_elements(By.XPATH,
                                          '//div[@class="whazf bD1FPe"]/descendant::div[@class="iSJ1kb va9cAf"]/ancestor::a["href"]')

    full_description = driver.find_elements(By.CLASS_NAME, 'HBvzbc')

    for web_element_buttons in full_description:
        if web_element_buttons.text == '':
            full_description.remove(web_element_buttons)

    for description in full_description:
        if any(word in description.text.lower() for word in AVOID_TERMS):
            continue

        elif all(word in description.text.lower() for word in SEARCH_TERMS):
            for button, href in zip(job_link_buttons, job_link_hrefs):
                if 'linkedin' in button.text.lower() or 'app.otta' in button.text.lower():
                    continue
                else:
                    job_posting_url = href.get_attribute('href')
                    JOB_LIST.append(job_title)
                    print(f'{len(JOB_LIST)}: {job_title.text} - {job_posting_url}')
                break


def test_ui_google_job_search(job_search_terms):

    # Search term entered for google search
    job_count = open_google_job_listings()
    job_listings = get_all_google_job_listing_names(job_count)
    driver.execute_script('arguments[0].scrollIntoView();', job_listings[0])
    for job_title in job_listings:
        if any(word in job_title.text.lower() for word in ['qa', 'test', 'tester', 'automation', 'python']):
            driver.execute_script('arguments[0].scrollIntoView();', job_title)
            driver.execute_script('arguments[0].click();', job_title)
            expand_full_descriptions()
            get_job_posting_link(job_title)


print(f'{len(JOB_LIST)} jobs found for the {job_search_terms} google search term')
