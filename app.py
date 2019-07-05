from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import pandas as pd
import os
import errno
from time import sleep

# from random import randint

# loading the json file and storing it as a dictionary
with open('triples.json') as fp:
    triples_dict = json.load(fp)

# defining globals
options = Options()
options.headless = True


def nrlm_scraper():
    driver = webdriver.Firefox(options=options)
    url = 'https://nrlm.gov.in/shgReport.do?methodName=showPage'
    driver.get(url)
    wait10 = WebDriverWait(driver, 10)
    wait10.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainex"]/tbody')))
    # locating the table for state values and storing all its row values
    state_table = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/table[2]/tbody')
    state_table_rows = state_table.find_elements_by_tag_name('tr')
    # iterating through the rows and accessing column values
    for state_table_row in state_table_rows:
        columns = state_table_row.find_elements_by_tag_name('td')
        if len(columns) > 1:
            if columns[1].text == 'JHARKHAND':
                columns[1].find_element_by_tag_name('a').click()
                break

    district_page(driver, wait10)


def district_page(driver, wait10):
    district = str.upper(input("Enter district name:"))
    if district in triples_dict.keys():
        search_box = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/div[2]/label/input')
        search_box.clear()
        search_box.send_keys(district)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/table/tbody/tr/td[2]/a').click()
            block_page(driver, wait10, district)
        except NoSuchElementException:
            print('No data for district {}'.format(district))


def block_page(driver, wait10, district):
    for block in triples_dict[district]:
        search_box = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/div[2]/label/input')
        search_box.clear()
        search_box.send_keys(block)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/table/tbody/tr/td[2]/a').click()
            panchayat_page(driver, wait10, district, block)
        except NoSuchElementException:
            print('No data for block {}'.format(block))


def panchayat_page(driver, wait10, district, block):
    print('Block:{}'.format(block))
    for panchayat in triples_dict[district][block]:
        search_box = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/div[2]/label/input')
        search_box.clear()
        search_box.send_keys(panchayat)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/table/tbody/tr[1]/td[2]/a').click()
            village_page(driver, wait10, block, panchayat)
        except NoSuchElementException:
            print('No data for panchayat {}'.format(panchayat))

    back_btn = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[1]/ul/li[2]/div/input[2]')
    back_btn.click()


def village_page(driver, wait10, block, panchayat):
    print('---->Panchayat: {}'.format(panchayat))
    entries_dd = Select(driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/div[1]/label/select'))
    entries_dd.select_by_visible_text('100')
    wait10.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/form/div[2]/div/div[3]/table/tbody')))
    village_table = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/table/tbody')
    village_table_rows = village_table.find_elements_by_tag_name('tr')
    village_temp = []

    for village_table_row in village_table_rows:
        columns = village_table_row.find_elements_by_tag_name('td')
        village_temp.append(columns[1].text)

    for village in village_temp:
        search_box = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/div[2]/label/input')
        search_box.clear()
        search_box.send_keys(village)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[3]/table/tbody/tr/td[2]/a').click()
            shg_page(driver, wait10, block, panchayat, village)
        except NoSuchElementException:
            print('---->No data for village {}'.format(village))

    back_btn = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[1]/ul/li[2]/div/input[2]')
    back_btn.click()


def shg_page(driver, wait10, block, panchayat, village):
    print('-------->Village: {}'.format(village))
    entries_dd = Select(driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/div[1]/label/select'))
    entries_dd.select_by_visible_text('100')
    wait10.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/form/div[2]/div/div[4]/table/tbody')))
    shg_table = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/table/tbody')
    shg_rows = shg_table.find_elements_by_tag_name('tr')
    shg_temp = []
    for shg_row in shg_rows:
        columns = shg_row.find_elements_by_tag_name('td')
        shg_temp.append(columns[1].text)

    for shg in shg_temp:
        wait10.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/form/div[2]/div/div[4]/div[2]/label/input')))
        search_box = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/div[2]/label/input')
        search_box.clear()
        search_box.send_keys(shg)
        try:
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/table/tbody/tr/td[2]/a').click()
            shg_details_page(driver, wait10, block, panchayat, village, shg)
        except NoSuchElementException:
            print('-------->No data for shg {}'.format(shg))

    back_btn = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[1]/ul/li[2]/div/input[2]')
    back_btn.click()


def shg_details_page(driver, wait10, block, panchayat, village, shg):
    print('------------>{}'.format(shg))
    try:
        entries_dd = Select(
            driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/div[1]/label/select'))
        entries_dd.select_by_visible_text('100')
        wait10.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/form/div[2]/div/div[4]/table/tbody')))
        shg_details = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[4]/table/tbody')
        rows = shg_details.find_elements_by_tag_name('tr')
        shg_details_downloader(rows, block, panchayat, village, shg)
    except NoSuchElementException:
        print('------------>Data not available')
    back_btn = driver.find_element_by_xpath('/html/body/div[4]/form/div[2]/div/div[1]/ul/li[2]/div/input[2]')
    back_btn.click()


def shg_details_downloader(rows, block, panchayat, village, shg):
    data = []
    for row in rows:
        columns = row.find_elements_by_tag_name('td')
        col1 = columns[0].text
        col2 = columns[1].text
        col3 = columns[2].text
        col4 = columns[3].text
        col5 = columns[4].text
        col6 = columns[5].text
        col7 = columns[6].text
        col8 = columns[7].text
        col9 = columns[8].text

        data.append([col1, col2, col3, col4, col5, col6, col7, col8, col9])

        df = pd.DataFrame(data=data,
                          columns=["Sl No", "Member's name", "Father's/Mother's Name", "Gender", "Category",
                                   "Disability",
                                   "Religion", "APL/BPL", "PIP category"])

        path = 'data/{}/{}/{}/'.format(block, panchayat, village)
        if not os.path.exists(path=path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        df.to_excel('{}{}.xlsx'.format(path, shg))


def main():
    nrlm_scraper()


if __name__ == '__main__':
    main()
