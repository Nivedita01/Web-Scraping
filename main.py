from Glassdoor_pagination import Glassdoor
import numpy as np
import Driver_Paths
from JobPortal_Common_Defs import JobPortal_Common
import logging
import psycopg2

logging.info("Starting, Job Search....")


logging.basicConfig(filename='scrapper.log', filemode='a',
                    format='%(asctime)s %(name)s - %(levelname)s - %(funcName)s- %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

conn = psycopg2.connect(
    host='',
    database='',
    user='',
    password=''
)
cur1 = conn.cursor()
cur1.execute('SELECT "job_title" FROM herokudjangoapp_jobs WHERE "job_title" IS NOT NULL')
job_title = cur1.fetchall()
print(list(job_title))
print(job_title)

job_title = np.fromiter([i[0] for i in job_title], dtype='<U50')
logging.info("Job titles")
logging.info(job_title)

cur1.execute('SELECT "job_location" FROM herokudjangoapp_jobs')
job_location = cur1.fetchall()
job_location = np.fromiter([i[0] for i in job_location], dtype='<U50')
logging.info(job_location)

'Create JobPortal_Common() object to access common functions'
jp_common = JobPortal_Common()
jp_common.time_to_execute()

browser_list = ["chrome", "gecko", "msedge"]

for i in range(job_title.size):
    driver = jp_common.driver_creation("chrome")
    gObj = Glassdoor(driver, Driver_Paths.glassdoor_url)
    jp_common.get_url(driver, gObj.url)
    for j in range(job_location.size):
        print("Searching for Job Title :: " + job_title[i])
        print("Searching for Job Location :: " + job_location[j])
        gObj.glassdoor_get_jobs(job_title[i], job_location[j], jp_common)
    jp_common.exit_browser(driver)

'Quit Browser'
logging.info(str(jp_common.time_to_execute()))