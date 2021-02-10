from datetime import datetime
from selenium.webdriver.common.by import By
import time
import re

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.support.ui import Select


class JobSite:
    job_email_list = []
    job_phoneNo_list = []
    driver = None
    url = ""
    flag = 0
    i = 0
    start_time = datetime.now()
    job_details = {'Job Category': '', 'Date Time Scrapped': '', 'Searched Job Title': '', 'Searched Job Location': '',
                   'Job Portal': 'Glassdoor',
                   'Job Date Posted': '', 'Job Title': '',
                   'Job Company Name': '', 'Job Location': '', 'Job Phone No': [], 'Job Email': '', 'Job Link': '',
                   'Job Description': ''}

    def __init__(self, driver, url):
        print(self.start_time)
        self.driver = driver
        self.url = url
        logging.basicConfig(filename='scrapper.log', filemode='a',
                            format='%(asctime)s %(name)s - %(levelname)s - %(funcName)s- %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
        print("*** Job Search***\n"
              "                  \n"
              "******************")
        print(url)

    def get_jobs(self, job_name, job_location, jp_common):
        print("Inside get_jobs")

        select = Select(self.driver.find_element_by_id('gt-tl'))
        select.select_by_value("hi")

        frame = self.driver.find_element_by_name("c")
        self.driver.switch_to.frame(frame)
        print("Switched to frame")

        see_jobs = self.driver.find_element_by_css_selector("b.link")
        see_jobs.click()
        print("See_jobs clicked")
        time.sleep(5)
        self.job_details['Searched Job Title'] = job_name
        if job_location == "Durham-Chapel Hill, NC":
            job_location = "Chapel Hill, NC"
        self.job_details['Searched Job Location'] = job_location
        time.sleep(1)
        self.job_details['Date Time Scrapped'] = datetime.now().strftime("%b-%m-%Y %H:%M:%S")

        last_day_value = self.search_jobs(job_name, job_location)
        print(last_day_value)
        if last_day_value == 1:
            pages_string = self.driver.find_element_by_css_selector('[data-test = page-x-of-y]').text.rpartition(" ")
            total_pages = pages_string[2]
            print("Total number of pages are : ", int(total_pages) - 2)
            for i in range(0, int(total_pages)):
                time.sleep(1)
                job_links = self.get_job_links(jp_common)
                if job_links:
                    self.job_details['Job Category'] = jp_common.set_job_category(job_name)
                    self.get_job_desc(job_links, jp_common)
                    i += 1
                    self.next_page()
        else:
            print("No jobs found in last 24 hours")

    def search_jobs(self, job_name, job_location):
        try:
            jobs_link = self.driver.find_element_by_css_selector("li.jobs")
            jobs_link.click()
            print("jobs clicked")
            title = self.driver.find_element_by_css_selector('[data-test = search-bar-keyword-input]')
            title.clear()
            print(title)
            title.send_keys(job_name, Keys.TAB)
            location = self.driver.find_element_by_css_selector('[data-test = search-bar-location-input]')
            location.clear()
            location.send_keys(job_location, Keys.ENTER)
            print("Inputs entered")
            time.sleep(3)
            try:
                whole_page = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#PageBodyContents')))
                if whole_page:
                    date_posted = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div#filter_fromAge')))
                    time.sleep(1.5)
                    date_posted.click()
                    time.sleep(1)
                    last_day = self.driver.find_element_by_css_selector("div#PrimaryDropdown > ul > li:nth-of-type(2)")
                    last_day_text = last_day.text.split("(")[0]
                    if last_day_text == 'Last Day':
                        flag = 1
                        last_day.click()
                        time.sleep(1)
                    else:
                        flag = 0
                        print("No jobs available in the last 24 hours for this location")
                else:
                    print("This is an error, not acceptable. Please report to developer. Results DOM not loaded.")
            except NoSuchElementException:
                flag = 0
                print("No jobs were found in the last 24 hours for this location")
                logging.error("No such element present")
            except ElementNotVisibleException:
                flag = 0
                print("No jobs were found in the last 24 hours for this location")
                logging.error("Element not visible")
            time.sleep(1)
        except Exception as e:
            print("Unknown Exception occurred", e)
            logging.error("Unknown Exception occurred  ", e)
        return flag

    def get_job_links(self, jp_common):
        print("In get_job_links")
        logging.info("In get_job_links")
        try:
            job_links_element = (self.driver.find_elements_by_css_selector(".jobInfoItem.jobTitle.jobLink"))
            return job_links_element
        except Exception as e:
            print("Unknown Exception in get_job_links", e)
            logging.exception(e)

    def get_job_desc(self, job_links, jp_common):
        logging.info("In get_job_desc")
        try:
            for link in job_links:
                link.click()
                try:
                    WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#prefix__icon-close-1")))
                    self.driver.find_element_by_css_selector("#prefix__icon-close-1").click()
                except:
                    print("Reading next record...")
                title = (link.find_element_by_css_selector("span")).text
                job_age = self.driver.find_element_by_css_selector('[data-test = job-age]').text
                job_company = self.driver.find_element_by_css_selector('.empWrapper .css-87uc0g').text
                time.sleep(1)
                job_description = self.driver.find_element_by_css_selector('#JobDescriptionContainer').text
                job_link = link.get_attribute('href')
                job_location = self.driver.find_element_by_css_selector('.empWrapper .css-56kyx5').text
                self.job_details["Job Title"] = title
                self.job_details['Job Company Name'] = job_company
                self.job_details['Job Description'] = job_description
                self.job_details['Job Email'] = jp_common.get_Email_desc(job_description)
                self.job_details['Job Link'] = job_link
                self.job_details['Job Location'] = job_location
                self.job_details['Job Phone No'] = jp_common.get_Phno_desc(job_description)
                self.job_details['Date Time Scrapped'] = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
                self.job_details['Job Date Posted'] = job_age
                if self.job_details['Job Email'] or self.job_details['Job Phone No']:
                    jp_common.write_to_csv(self.job_details)
        except Exception as e:
            logging.error("Unknown exception in get_job_desc")
            logging.exception(e)

    def next_page(self):
        try:
            web_element = WebDriverWait(self.driver, 1).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#FooterPageNav span')))
            length = len(web_element)
            if web_element[length - 1].get_attribute("class") == "disabled":
                page_count = False
            else:
                web_element[length - 1].click()
        except Exception as e:
            print("No Next page")
            page_count = False

    def get_Phno_desc(self, job_desc):
        job_phoneNo_list = []
        try:
            # Get phone and store
            phoneNo_match = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}|[+][1]\s[0-9]{3}\s[0-9]{3}\s[0-9]{4}|'
                                       r'[(][0-9]{3}[)]\s[0-9]{3}-[0-9]{4}', job_desc)
            for phoneNo in phoneNo_match:
                ph = self.driver.find_element_by_xpath("//*[contains(text()," + phoneNo + "]")
                parent = self.driver.execute_script("return arguments[0].parentNode;", ph)
                if phoneNo not in self.job_phoneNo_list:
                    self.job_phoneNo_list.append(phoneNo)
        except Exception as e:
            logging.error("Exception in Class:JobPortal_Common def:get_Email_desc", e)
        else:
            return phoneNo_match

    def get_Email_desc(self, job_desc):
        email_list = []
        try:
            email_match = re.findall(r'[\w\.-]+@[\w\.-]+', job_desc)
            for email in email_match:
                if email not in self.job_email_list:
                    if not (re.search('accommodation', email, re.IGNORECASE) or re.search('disabilit', email,
                                                                                          re.IGNORECASE) or re.search(
                            'employeeservice', email, re.IGNORECASE)):
                        email_list.append(email)
                        self.job_email_list.append(email)
        except Exception as e:
            logging.error("Exception in Class:JobPortal_Common def:get_Email_desc", e)
        else:
            return email_list
