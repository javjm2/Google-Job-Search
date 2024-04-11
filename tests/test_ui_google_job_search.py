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
sdet = 'software+development+engineer+in+test+jobs'
senior_automation_tester = 'senior+automation+tester+jobs'
senior_test_automation_engineer = 'senior+test+automation+engineer+jobs'
automation_tester = 'automation+tester+jobs'
test_automation_engineer = 'test+automation_engineer+jobs'
qa_automation_engineer = 'qa+automation_engineer+jobs'
lead_qa_automation_engineer = 'lead+qa+automation_engineer+jobs'
lead_automation_engineer = 'lead+automation_engineer+jobs'
senior_qa_engineer = 'senior+qa+engineer+jobs'
qa_engineer = 'qa+engineer+jobs'
qa_data_test_engineer = 'qa+data_test+engineer'


# Remote first job search terms
remote_test_automation_engineer = 'test+automation_engineer+remote+first+jobs'
remote_senior_qa_engineer = 'senior+qa+engineer+remote+first+jobs'
remote_sdet = 'software+development+engineer+in+test+remote+first+jobs'

# Contract Jobs
automation_tester_contract = 'automation+tester+contract'
test_automation_engineer_contract = 'test+automation_engineer+contract+jobs'
sdet_contract = 'software+development+engineer+in+test+contract+jobs'
senior_qa_engineer_contract = 'senior+qa engineer+contract+jobs'
qa_engineer_contract = 'qa+engineer+contract+jobs'
test_engineer_contract = 'test+engineer+contract+jobs'
system_tester_contract = 'system_tester_contract_jobs'

# Search terms for job description
search_terms = ['python']
# avoid_terms = []
avoid_terms = ['on-site', 'onsite', 'offices', 'office', 'hybrid']


@pytest.fixture(params=[remote_test_automation_engineer, remote_senior_qa_engineer, remote_sdet])
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


def open_google_job_listings(job_search):
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
    all_descriptions_buttons = driver.find_elements(By.XPATH, '//*[contains(text(), "Show full description")]')

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
        if any(word in description.text.lower() for word in avoid_terms):
            continue

        elif all(word in description.text.lower() for word in search_terms):
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
    job_count = open_google_job_listings(job_search_terms)
    job_listings = get_all_google_job_listing_names(job_count)
    driver.execute_script('arguments[0].scrollIntoView();', job_listings[0])
    for job_title in job_listings:
        if any(word in job_title.text.lower() for word in ['qa', 'test', 'tester', 'automation', 'python']):
            driver.execute_script('arguments[0].scrollIntoView();', job_title)
            driver.execute_script('arguments[0].click();', job_title)
            expand_full_descriptions()
            get_job_posting_link(job_title)


print(f'{len(JOB_LIST)} jobs found for the {job_search_terms} google search term')
