"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 03-11-20
    * description:This script extracts the corresponding undergraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/ACAP_courses_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/ACAP_courses.csv'

course_data = {'Level_Code': '', 'University': 'Australian College of Applied Psychology', 'City': '',
               'Country': 'Australia', 'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD',
               'Currency_Time': 'year', 'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '',
               'Prerequisite_1': '', 'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '',
               'Prerequisite_2_grade': '6.5', 'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '',
               'Availability': 'A', 'Description': '','Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '',
               'Face_to_Face': '', 'Blended': '', 'Remarks': ''}

possible_cities = {
                   'online': 'Online', 'mixed': 'Online', 'brisbane': 'Brisbane', 'sydney': 'Sydney',
                   'melbourne': 'Melbourne', 'perth': 'Perth'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    title_tag = soup.find('h1', class_='h2')
    if title_tag:
        course_data['Course'] = title_tag.get_text()
        print('COURSE TITLE: ', course_data['Course'])


        # DECIDE THE LEVEL CODE
        for i in level_key:
            for j in level_key[i]:
                if j in course_data['Course']:
                    course_data['Level_Code'] = i
        print('COURSE LEVEL CODE: ', course_data['Level_Code'])

        # DECIDE THE FACULTY
        for i in faculty_key:
            for j in faculty_key[i]:
                if j.lower() in course_data['Course'].lower():
                    course_data['Faculty'] = i
        print('COURSE FACULTY: ', course_data['Faculty'])

        # COURSE LANGUAGE
        for language in possible_languages:
            if language in course_data['Course']:
                course_data['Course_Lang'] = language
            else:
                course_data['Course_Lang'] = 'English'
        print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # COURSE DESCRIPTION
    desc_tag = soup.find('h2', class_='h3 has-accent', text=re.compile('About this course', re.IGNORECASE))
    if desc_tag:
        desc_list = []
        desc_p = desc_tag.find_next_siblings('p')
        if desc_p:
            for p in desc_p:
                desc_list.append(p.get_text().strip())
            desc_list = ' '.join(desc_list)
            course_data['Description'] = desc_list
            print('COURSE DESCRIPTION: ', course_data['Description'])

    # DURATION
    dura_title = soup.find('label', text=re.compile('Course Length', re.IGNORECASE))
    if dura_title:
        dura_p = dura_title.find_next_sibling('p')
        if dura_p:
            dura_text = dura_p.get_text().lower()
            if 'full-time' in dura_text:
                course_data['Full_Time'] = 'yes'
            else:
                course_data['Full_Time'] = 'no'
            if 'part-time' in dura_text:
                course_data['Part_Time'] = 'yes'
            else:
                course_data['Part_Time'] = 'no'
            converted_duration = dura.convert_duration(dura_p.get_text())
            if converted_duration is not None:
                duration_l = list(converted_duration)
                if duration_l[0] == 1 and 'Years' in duration_l[1]:
                    duration_l[1] = 'Year'
                if duration_l[0] == 1 and 'Months' in duration_l[1]:
                    duration_l[1] = 'Month'
                course_data['Duration'] = duration_l[0]
                course_data['Duration_Time'] = duration_l[1]
                print('COURSE DURATION: ', str(duration_l[0]) + ' / ' + duration_l[1])
            print('FULL-TIME/PART-TIME: ', course_data['Full_Time'] + ' / ' + course_data['Part_Time'])

    # DELIVERY / CITY
    deli_title = soup.find('label', text=re.compile('Study Modes', re.IGNORECASE))
    if deli_title:
        deli_p = deli_title.find_next_sibling('p')
        if deli_p:
            deli_text = deli_p.get_text().lower()
            if 'online' in deli_text:
                course_data['Online'] = 'yes'
                actual_cities.append('online')
            else:
                course_data['Online'] = 'no'
            if 'face-to-face' in deli_text:
                course_data['Face_to_Face'] = 'yes'
            else:
                course_data['Face_to_Face'] = 'no'
            if 'on campus' in deli_text or 'on-campus' in deli_text:
                course_data['Face_to_Face'] = 'yes'
                course_data['Offline'] = 'yes'
            else:
                course_data['Face_to_Face'] = 'no'
                course_data['Offline'] = 'no'
            if 'blended' in deli_text:
                course_data['Blended'] = 'yes'
            else:
                course_data['Blended'] = 'no'
            if 'perth' in deli_text:
                actual_cities.append('perth')
            if 'melbourne' in deli_text:
                actual_cities.append('melbourne')
            if 'brisbane' in deli_text:
                actual_cities.append('brisbane')
            if 'sydney' in deli_text:
                actual_cities.append('sydney')
            print('DELIVERY: online: ' + course_data['Online'] + ' offline: ' + course_data['Offline'] +
                  ' face to face: ' + course_data['Face_to_Face'] + ' blended: ' + course_data['Blended'] +
                  ' distance: ' + course_data['Distance'])
            print('CITY: ', actual_cities)
    # FEES
    fees_title = soup.find('label', text=re.compile('Fees', re.IGNORECASE))
    if fees_title:
        fees_temp_list = []
        fees_p = fees_title.find_next_sibling('p')
        if fees_p:
            fees_span_list = fees_p.find_all('span')
            for span in fees_span_list:
                fees_list = re.findall(r'\d+', span.get_text())
                if fees_list is not None:
                    if len(fees_list) == 2:
                        full_fee = int(fees_list[0]) * int(fees_list[1])
                        course_data['Int_Fees'] = full_fee
                    elif len(fees_list) == 1:
                        fees_temp_list.append(fees_list[0])
                if len(fees_temp_list) == 2:
                    full_fee = int(fees_temp_list[0]) * int(fees_temp_list[1])
                    course_data['Int_Fees'] = full_fee
            print('INT FEE: ', course_data['Int_Fees'])

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face', 'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('ACAP_courses_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)





