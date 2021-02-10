import csv
import datetime
import json
import logging
import re
import smtplib
import ssl
import sys
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path

import pandas
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

import Driver_Paths


class JobPortal_Common:
    driver = None
    job_email_list = []
    job_phoneNo_list = []
    start_time = datetime.datetime.now()
    logger = ''
    browser = ''

    logging.basicConfig(filename='scrapper.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    def __init__(self):
        print("JobPortal_Common_Defs Initialised")
        print("Started at:", self.start_time)

        logging.basicConfig(filename='scrapper.log', filemode='a',
                            format='%(asctime)s %(name)s - %(levelname)s - %(funcName)s- %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

        if path.exists('Jobs_Scrapped_new.csv'):
            print("Jobs_Scrapped_new.csv exists")
        else:
            with open('Jobs_Scrapped_new.csv', mode='w', encoding='utf-8', newline='') as jobs:
                fieldnames = ['Job Category', 'Date Time Scrapped', 'Searched Job Title', 'Searched Job Location',
                              'Job Portal',
                              'Job Date Posted', 'Job Title',
                              'Company Name', 'Job Location', 'Job Phone No', 'Job Email', 'Job Link',
                              'Job Description']
                jobs_writer = csv.DictWriter(jobs, fieldnames=fieldnames, delimiter=',', quotechar='"',
                                             quoting=csv.QUOTE_MINIMAL)
                jobs_writer.writeheader()
                print("Jobs_Scrapped_new.csv created")

    def write_to_csv(self, dict_name):
        print("Inside write_to_csv")
        with open('Jobs_Scrapped_new.csv', mode='a+', encoding='utf-8', newline='') as jobs:
            fieldnames = ['Job Category', 'Date Time Scrapped', 'Searched Job Title', 'Searched Job Location',
                          'Job Portal',
                          'Job Date Posted', 'Job Title',
                          'Job Company Name', 'Job Location', 'Job Phone No', 'Job Email', 'Job Link',
                          'Job Description']
            jobs_writer = csv.DictWriter(jobs, fieldnames=fieldnames, delimiter=',', quotechar='"',
                                         quoting=csv.QUOTE_MINIMAL)
            jobs_writer.writerow(dict_name)
            print("write_to_csv Success")

    def convert_csv_to_pandas(self, csv_filename, index_col):
        df = pandas.read_csv(csv_filename, index_col=index_col)
        return df

    def query_df(self, df, index):
        df = pandas.read_csv('JobTitleList.csv', index_col='Job Label')
        print(df)

    def get_driver(self, browser):
        print("Trying to open browser in Common defs")
        if (browser == "chrome"):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--ignore-certificates-errors')
                options.add_argument("--test-type")
                options.add_argument("start-maximized")
                self.driver = webdriver.Chrome(executable_path=Driver_Paths.chrome_driver_path, options=options)
                self.driver.maximize_window()
                time.sleep(3)
                print("Browser opened successfully")
                logging.info("Browser opened successfully")

            except Exception as e:
                logging.exception("Browser closed unexpectedly")
                logging.exception(e)
                print("Browser closed unexpectedly, hence the script stopped.")

        elif browser == "gecko":
            try:
                options = webdriver.FirefoxOptions()
                options.add_argument("-start-maximized")
                caps = DesiredCapabilities().FIREFOX
                caps["marionette"] = True
                self.driver = webdriver.Firefox(executable_path=Driver_Paths.gecko_driver_path, options=options,
                                                capabilities=caps)
                self.driver.maximize_window()
                time.sleep(0.5)
                logging.info("Browser opened successfully")
            except Exception as e:
                logging.exception("Browser closed unexpectedly")
                logging.exception(e)
                print("Browser closed unexpectedly, hence the script stopped.")

        return self.driver

    def driver_creation(self, browser):
        self.browser = browser
        driver = self.get_driver(browser)

        for i in range(5):
            while driver is None:
                if i < 5:
                    print("Opening Browser, Attempts:", i + 1, "/5 times")
                    driver = self.get_driver(browser)
                    time.sleep(1)
                    i += 1
                    if driver is not None:
                        break
        return driver

    def get_url(self, driver, url):
        print("IN get_url in common defs")
        try:
            for attempts in range(5):
                if driver is not None:
                    try:
                        driver.delete_all_cookies()
                        driver.get(url)
                        time.sleep(0.5)
                        # time.sleep(3)
                        if driver.current_url == url:
                            print(driver.title)
                            print(driver.current_url)
                            break
                    except Exception as e:
                        print("Trying to open ", url, attempts + 1, "/5 times")
                        driver.get_screenshot_as_file("openUrlFailure.png")
                        print(e)
                        attempts += 1
                else:
                    self.driver_creation(self.browser)
            if (attempts == 4):
                sys.exit()
        except Exception as e:
            print("Error occurred when getting url in get_url", e)
            logging.exception("Error occurred when getting url in get_url")
            logging.exception(e)
            sys.exit()

    # Set Job Category
    def set_job_category(self, job_title):
        arr1 = ['Python Developer', 'Python DJango', 'Python Django Developer', 'Python', 'Developer']
        arr2 = ['SDET', 'QA', 'QA Automation', 'Manual Testing']
        arr3 = ['Java Developer', 'Java', 'Java Programmer']
        arr4 = ['Data Science', 'Data Scientist', 'Data Engineer']
        print(job_title)

        if any(re.findall('|'.join(arr1), job_title)):
            return "Python/Django Developer"
        elif any(re.findall('|'.join(arr2), job_title)):
            return "QA"
        elif any(re.findall('|'.join(arr3), job_title)):
            return "SDET"
        elif any(re.findall('|'.join(arr4), job_title)):
            return "Data Science"
        else:
            return "Not Mentioned"

    # Search email from job description and store
    def get_Email(self, text, job_email_list):
        email_match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        for email in email_match:
            if email not in job_email_list:
                job_email_list.append(email)
                print(email)
        return job_email_list

    # Search email from job description and store
    def get_Email_desc(self, job_desc):
        email_list = []
        try:
            # print(job_desc)
            email_match = re.findall(r'[\w\.-]+@[\w\.-]+', job_desc)
            for email in email_match:
                if email not in self.job_email_list:
                    # if not ("accommodation" in email or "disabilit" in email or "employeeservice" in email ):
                    if not (re.search('accommodation', email, re.IGNORECASE) or re.search('disabilit', email,
                                                                                          re.IGNORECASE) or re.search(
                                                                                            'employeeservice', email, re.IGNORECASE)):
                        email_list.append(email)
                        self.job_email_list.append(email)
                        print(email)
        except Exception as e:
            print("Exception in Class:JobPortal_Common def:get_Email_desc", e)
            logging.error("Exception in Class:JobPortal_Common def:get_Email_desc", e)
            # breakpoint()
        else:
            return email_list

    # Search Phone no from job description and store
    def get_Phno(self, text, job_phoneNo_list):
        # Get phone and store
        phoneNo_match = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', text)
        for phoneNo in phoneNo_match:
            if phoneNo not in job_phoneNo_list:
                job_phoneNo_list.append(phoneNo)
                print(phoneNo)

        return job_phoneNo_list

    """ Search Phone no from job description
    Following formats covered in regex:
    (541) 754 - 3010        Domestic
    +1 - 541 - 754 - 3010   International
    1 - 541 - 754 - 3010    Dialed in the US"""

    def get_Phno_desc(self, job_desc):

        try:
            # Get phone and store
            phoneNo_match = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}|[+][1]\s[0-9]{3}\s[0-9]{3}\s[0-9]{4}|'
                                       r'[(][0-9]{3}[)]\s[0-9]{3}-[0-9]{4}', job_desc)
            # phoneNo_match = re.findall(r'[0-9]{3}-[0-9]{3}-[0-9]{4}', job_desc)
            for phoneNo in phoneNo_match:
                if phoneNo not in self.job_phoneNo_list:
                    self.job_phoneNo_list.append(phoneNo)
                    print(phoneNo)
        except Exception as e:
            print("Exception in Class:JobPortal_Common def:get_Email_desc", e)
            logging.error("Exception in Class:JobPortal_Common def:get_Email_desc", e)
        else:
            return phoneNo_match

    # Copy to json file
    def copy_to_json(self, filename, details_list):
        print("In copy_to_json Common defs")
        details = json.dumps(details_list)
        print(details)
        loaded_json = json.loads(details)
        print(loaded_json)
        with open(filename, 'w') as json_file:
            json.dump(loaded_json, json_file)

    # Copy to json file
    def copy_to_json(self, filename, details_dict):
        print("In copy_to_json Common defs")
        res_dict = {details_dict[i]: details_dict[i + 1] for i in range(0, len(details_dict), 2)}

        newf = open(filename, 'r')
        news1 = newf.read()
        dict1 = json.loads(news1)
        temp = dict1
        temp.update(res_dict)
        with open(filename, 'w') as json_file:
            json.dump(temp, json_file)

    # Extracts dta from JSON file and saves it on Python object
    def json_to_obj(self, filename):
        """Extracts dta from JSON file and saves it on Python object"""
        print("json to obj")
        obj = None
        with open(filename, 'r') as json_file:
            obj = json.loads(json_file.read())
            return obj

    # Print all phone numbers from list
    def get_all_phno(self):
        print("phone nos: ", len(self.job_phoneNo_list), " ", self.job_phoneNo_list)
        logging.info("phone nos: " + str(len(self.job_phoneNo_list)) + " " + str(self.job_phoneNo_list))

    # Print all email from list
    def get_all_email(self):
        print("emails :", len(self.job_email_list), " ", self.job_email_list)
        logging.info("emails :" + str(len(self.job_email_list)) + " " + str(self.job_email_list))

    # Calculate time taken to execute
    def time_to_execute(self):
        end_time = datetime.datetime.now()
        # print(end_time)
        return end_time - self.start_time

    # Close the browser
    def end_search(self):
        self.driver.close()

    # Quit browser
    def exit_browser(self, driver):
        driver.quit()

    def datePosted(self, dateposted):
        sentences = dateposted.find("ago")
        return dateposted[sentences - 8:sentences + 3]

    def find_web_element(self, xpath, element_desc, element_count, wait):
        web_element = ''
        try:
            if element_count == "one":
                try:
                    if element_desc == "Set 100":
                        web_element = Select(wait.until(EC.presence_of_element_located((By.XPATH, xpath))))
                    else:
                        web_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    print(element_desc, "found")
                    logging.info(element_desc + " found")
                    return web_element
                except Exception as e:
                    print(element_desc + " not found", e)
                    logging.exception("Exception Occurred when fetching element " + element_desc)
                    logging.exception(e)
            elif element_count == "multiple":
                try:
                    web_element = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
                    print(element_desc, "found and returned list of web elements")
                    logging.info("Found and returned list of web elements " + element_desc)
                    return web_element
                except Exception as e:
                    print(element_desc, "not found", e)
                    logging.exception("Unexpected Exception raised when fetching list of web elements " + element_desc)
                    logging.exception(e)

        except Exception as e:
            print("error in find web element ", e)
            logging.error("Unexpected Exception raised in find_web_element " + element_desc)
            logging.exception(e)


    def find_web_element_css(self, css, element_desc, element_count, wait):
        try:
            if element_count == "one":
                try:
                    if element_desc == "Set 100":
                        web_element = Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css))))
                    else:
                        web_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
                    print(element_desc, "found")
                    logging.info(element_desc + " found")
                    return web_element
                except Exception as e:
                    print(element_desc + " not found", e)
                    logging.exception("Exception Occurred when fetching element " + element_desc)
                    logging.exception(e)
            elif element_count == "multiple":
                try:
                    web_element = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css)))
                    print(element_desc, "found and returned list of web elements")
                    logging.info("Found and returned list of web elements " + element_desc)
                    return web_element
                except Exception as e:
                    print(element_desc, "not found", e)
                    logging.exception("Unexpected Exception raised when fetching list of web elements " + element_desc)
                    logging.exception(e)
        except Exception as e:
            print("error in find web element ", e)
            logging.error("Unexpected Exception raised in find_web_element " + element_desc)
            logging.exception(e)

    def web_element_action(self, web_element, action, send_keys_values, element_desc):
        try:
            if action == "send_keys":
                try:
                    web_element.clear()
                    web_element.send_keys(send_keys_values)
                    print(action, "to", element_desc)
                    logging.info(action + " to " + element_desc)
                except Exception as e:
                    print("Unexpected Exception raised when", action, "to", element_desc, e)
                    logging.exception("Unexpected Exception raised when", action, "to" + element_desc)
                    logging.exception(e)
            elif action == "select":
                try:
                    web_element.select_by_visible_text('100')
                    print(action, "to", element_desc)
                    logging.info(action + " to " + element_desc)
                except Exception as e:
                    print("Unexpected Exception raised when", action, "to", element_desc, e)
                    logging.exception("Unexpected Exception raised when", action, "to" + element_desc)
                    logging.exception(e)
            elif action == "click":
                try:
                    web_element.click()
                    print(element_desc, "clicked")
                    logging.info(element_desc + " clicked")
                except Exception as e:
                    print("Unexpected error while clicking", element_desc, e)
                    logging.exception("Unexpected error while clicking " + element_desc)
                    logging.exception(e)
            elif action == "get_text":
                try:
                    print(element_desc, "get_text")
                    logging.info(element_desc + " clicked")
                    print(web_element.get_attribute('text'))
                    return web_element.get_attribute('text')
                except Exception as e:
                    print("Unexpected error while getting text ", element_desc, e)
                    logging.exception("Unexpected error while getting text" + element_desc)
                    logging.exception(e)
        except Exception as e:
            print("Unexpected exception occurred in def web_element_action", e)
            logging.error("Unexpected exception occurred in def")
            logging.exception(e)

    def delete_duplicate_entries(self, job1, job2):
        a = set(job1.split())
        b = set(job2.split())
        c = a.intersection(b)
        if (float(len(c)) / (len(a) + len(b) - len(c))) == 1:
            print("same entries found", job1, job2)

    def job_categorisation(self, job_arr):
        job_arr = job_arr.strip('"')
        keywords_dict = {"Testing": ["sdet", "qa", "qa automation", "software developer in test", "qa analyst"],
                         "java developer":
                             ["java developer", "developer", "full stack java developer", "Devops engineer",
                              "java api developer", "java",
                              "java liferay developer", "angular"],
                         "python developer": ["django", "python django developer", "python", "flask",
                                              "python developer", "backend", "developer"]}
        for keys in keywords_dict:
            if job_arr in keywords_dict[keys]:
                return keys
