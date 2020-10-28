import configparser
from datetime import datetime
import requests
import pprint
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import re

#applied_jobs_filename = "applied_jobs.json"
#unapplied_jobs_filename = "unapplied_jobs.json"
#queued_jobs_filename = "queued_jobs.json"
#logfile_filename = "logfile.txt"

config = configparser.ConfigParser()
config.read('config.ini')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
jobfile = config['Files'].get('jobs_filename')
with open(jobfile, 'r') as j:
    jobsDict = json.load(j)

def log(message):
    with open(config['Files'].get('logfile_filename'), 'a') as logfile:
        now = datetime.now()
        timestamp = now.strftime("%Y/%m/%d %H:%M:%S - ")
        print(timestamp + message, file=logfile)

def logUnapplied(urlId, email="N/A"):
    #append url
    doneSet.add(urlId)
    jobsDict['Unapplied'][urlId] = {'Email': email}
    with open(jobfile, 'w') as j:
        json.dump(jobsDict, j)

def getEmail(url):
    urlId = re.search("[0-9]+$", url).group(0)
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=chrome_options)
    driver.get(url)
    button = driver.find_elements_by_id("applynowbutton")
    title = driver.find_elements_by_css_selector('[property=title]')[0].text
    employer = driver.find_elements_by_css_selector('[property=hiringOrganization]')[0].text
    jobSource = driver.find_elements_by_css_selector('span.source-image')[0].text
    jobBankId = driver.find_elements_by_css_selector('span.source-image+span')[0].text
    if len(button) > 0:# change this to try/catch
       button[0].click();
       time.sleep(2)
       howToApply = driver.find_elements_by_id("howtoapply");
       if len(howToApply) > 0:
           email = howToApply[0].text.partition("email\n")[2].partition("\n")[0]
           enqueueJob(urlId, title, employer, jobSource, jobBankId, email)
       else:
           logUnapplied(urlId);
    else:
        logUnapplied(urlId);

def enqueueJob(urlId, title, employer, jobSource, jobBankId, email):
    doneSet.add(urlId)
    #in subject/body lines, the following key terms are to be replaced by the appropriate job details: %t=title, %e=employer, %s=job source, %i=post ID number
    subject = config['email'].get('subject')
    message = config['email'].get('body')
    jobsDict['Queued'][urlId] = {'email': email, 'subject': subject, 'message':message}
    with open(jobfile, 'w') as j:
        json.dump(jobsDict, j)


doneSet = set()
try:
    with open(jobfile, 'r') as j:
        jobsDict = json.load(j)
        for section in jobsDict.keys():
            for job in jobsDict[section].keys():
                doneSet.add(job)
except FileNotFoundError :
    with open(jobsDict, 'w') as j:
        jobsDict = {'Applied': {}, 'Unapplied': {}, 'Queued': {}}
        json.dump(jobsDict, j)

#URL = 'https://www.jobbank.gc.ca/jobsearch/jobsearch?fage=30&fn=0131&fn=2147&fn=2281&fn=7246&term=network&sort=M&fprov=ON'
URL = config['Job Banks'].get('jobbank.ca_search_urls')
page = requests.get(URL)
print("Running query...")
soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id='result_block')
job_elems = results.find_all('article')
link_list = []
for job_elem in job_elems:
  link = job_elem.find('a')['href']
  link_list.append("https://www.jobbank.gc.ca" + link.split(";", 1)[0])
log(str(len(link_list)) + " jobs found.")
applicationCount = 0
for jobLink in link_list:
    urlId = re.search("[0-9]+$", jobLink).group(0)
    if urlId not in doneSet:
        getEmail(jobLink);
        applicationCount += 1
log(str(len(link_list) - applicationCount) + " duplicates dropped, " + str(applicationCount) + " job emails enqueued.")

