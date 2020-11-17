"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 17-11-20
    * description:This script extracts all the courses links and save it in txt file.
"""
from pathlib import Path
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os


option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# MAIN ROUTINE
courses_page_url = 'https://www.acap.edu.au/courses/'
site_url = 'https://www.acap.edu.au'
list_of_links = []
browser.get(courses_page_url)
page_url = browser.page_source
soup = BeautifulSoup(page_url, 'lxml')
delay_ = 5  # seconds

# EXTRACT ALL THE LINKS TO LIST
result_elements = soup.find_all('div', attrs={"class": "row course-list"})
for element in result_elements:
    links = element.find_all('a', href=True)
    for link in links:
        if link:
            link_href = link['href']
            full_link = urljoin(site_url, link_href)
            list_of_links.append(full_link)

# SAVE TO FILE
course_links_file_path = os.getcwd().replace('\\', '/') + '/ACAP_courses_links.txt'
course_links_file = open(course_links_file_path, 'w')
for link in list_of_links:
    if link is not None and link != "" and link != "\n":
        if link == list_of_links[-1]:
            course_links_file.write(link.strip())
        else:
            course_links_file.write(link.strip() + '\n')
course_links_file.close()
