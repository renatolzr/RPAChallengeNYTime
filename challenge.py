import os
import re
import logging
import pandas as pd
import time
import configparser
import util
from selenium_util import SeleniumLayer
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Definicion de Carpetas
dir_path = os.path.dirname(__file__)
dir_in = os.path.join(dir_path, "input")
dir_out = os.path.join(dir_path, "output")
dir_log = os.path.join(dir_path, "log")
util.create_folder_env(dir_path)

# Definicion de Variables
today = datetime.now()
today_line = str(today.strftime("%Y%m%d%H%M%S"))
today_format = str(today.strftime("%d/%m/%Y %H:%M:%S"))
today_date = str(today.strftime("%d/%m/%Y"))
file_mockup = os.path.join(dir_in, 'mockup.xlsx')
# Loggin file
file_log = os.path.join(dir_log, 'challenge_' + today_line + ".log")
log = util.config_logging(file_log, logging.DEBUG, True)
se = SeleniumLayer(log, dir_in, dir_path, dir_out)

# Config File
config = configparser.ConfigParser()
config.optionxform = str
config.read('config.ini')
config.__dict__.update(config.items('DEFAULT'))


def create_dataframe(data, columns):
    df = pd.DataFrame(data=data, columns=columns)
    return df


def get_periods():
    date_end = datetime.today()
    if (config.periods in ['0', '1']):
        date_start = date_end.replace(day=1)
    elif (config.periods in ['2']):
        date_start = date_end - relativedelta(month=1)
    elif (config.periods in ['3']):
        date_start = date_end - relativedelta(month=2)
    else:
        date_start = date_end - relativedelta(month=int(config.periods))

    return date_start, date_end


def seach_by_webcontrols():
    query = config.search_phrase
    date_start, date_end = get_periods()

    if (se.check_exists_visible_element_by_xpath(
            '//*[@id="complianceOverlay"]//button')):
        se.click_visible_element_by_xpath(
            '//*[@id="complianceOverlay"]//button')

    se.click_visible_element_by_xpath(
        '//*[@id="app"]//button[@aria-controls="search-input"]')
    if (se.check_exists_visible_element_by_name('query')):
        se.send_key_visible_element_by_name('query', query)
        se.click_visible_element_by_xpath('//form[@action="/search"]//button')

    se.click_visible_element_by_xpath(
        '//*[@id="site-content"]//div[@aria-label="Date Range"]/button')
    se.click_visible_element_by_xpath(
        '//*[@id="site-content"]//button[@aria-label="Specific Dates"]')

    se.send_key_visible_element_by_id('startDate', date_start)
    se.send_key_visible_element_by_id('endDate', date_end)
    se.send_key_visible_element_by_id('endDate', Keys.ENTER)

    if (se.check_exists_visible_element_by_xpath(
            '//*[@id="site-content"]//select')):
        se.select_by_value_located_by_xpath(
            '//*[@id="site-content"]//select', 'newest')


def seach_by_url():
    log.debug('Get periods from config file')
    date_start, date_end = get_periods()
    query = config.search_phrase
    log.debug(f'Apply filter {query}')
    date_end = date_end.strftime("%Y-%m-%d")
    date_start = date_start.strftime("%Y-%m-%d")
    log.debug(f'Filter by {date_start} to {date_end}')

    if (se.check_exists_visible_element_by_xpath(
            '//*[@id="complianceOverlay"]//button')):
        se.click_visible_element_by_xpath(
            '//*[@id="complianceOverlay"]//button')
    se.navegar_url_chrome(
        f"https://www.nytimes.com/search?dropmab=false&endDate={date_end}&query={query}&sort=newest&startDate={date_start}")


def filter_news():
    categeories = config.news_type.split(",")
    sections = config.section.split(",")
    log.debug(f'Get categories {categeories}')
    se.click_visible_element_by_xpath(
        '//div[@data-testid="section"]//button[@data-testid="search-multiselect-button"]')

    for section in sections:
        log.debug(f'Pick section {section}')
        if (not se.check_checkbox_is_selected_by_xpath(
                f'//*[@id="site-content"]//input[contains(@value,"{section}")]')):
            se.click_visible_element_by_xpath(
                f'//*[@id="site-content"]//input[contains(@value,"{section}")]')
            log.debug(f'Section {section} selected')
        if str(section).lower() == 'any':
            log.debug(f'Section {section} selected')
            break

    se.click_visible_element_by_xpath(
        '//div[@data-testid="section"]//button[@data-testid="search-multiselect-button"]')
    log.debug('Apply section fiters')

    log.debug(f'Get sections {sections}')
    se.click_visible_element_by_xpath(
        '//div[@data-testid="type"]//button[@data-testid="search-multiselect-button"]')

    for category in categeories:
        category = str(category).lower()
        log.debug(f'Pick category {category}')
        if (not se.check_checkbox_is_selected_by_xpath(
                f'//*[@id="site-content"]//input[contains(@value,"{category}")]')):
            se.click_visible_element_by_xpath(
                f'//*[@id="site-content"]//input[contains(@value,"{category}")]')
            log.debug(f'Category {category} selected')
        if category == 'any':
            log.debug(f'Category {category} selected')
            break
    log.debug('Apply category fiters')
    se.click_visible_element_by_xpath(
        '//div[@data-testid="type"]//button[@data-testid="search-multiselect-button"]')


def get_news():
    log.debug('Init data for dataframe')
    data = []
    columns = [
        'title',
        'date',
        'description',
        'picture filename',
        'count',
        'money']
    log.debug('Get News list')
    list_news = se.get_exists_visible_element_by_xpath(
        '//*[@id="site-content"]//ol[@data-testid="search-results"]/li')
    pattern = r'\$[0-9]+(\.[0-9]{2})? | [0-9]+ dollars | [0-9]+ USD'
    log.debug('Set patter for money')
    i = 1
    for new in list_news:
        log.debug('Extract new')
        text = se.get_text_element(new)
        lines = text.split('\n')
        if len(lines) >= 3:
            image_path = dir_out + '/' + str(i) + '.png'
            log.debug('Download image')
            if se.check_exists_visible_element_by_xpath(
                    f'//*[@id="site-content"]//ol[@data-testid="search-results"]//li[{i}]//img'):
                se.download_imagen_by_xpath(
                    f'//li[{i}]//img', image_path, new)
            matches = re.findall(pattern, text)
            new_data = [
                lines[2],
                lines[0],
                lines[3],
                image_path,
                text.count(
                    config.search_phrase),
                len(matches)>0]
            log.debug(f'Set new {new_data}')
            data.append(new_data)

        i += 1
    return data, columns


def main():
    log.debug('Init bot')
    search_by_url = bool(config.search_method)
    log.debug('Init Chrome driver')
    se.iniciar_driver_chrome()
    log.debug('Navigate to URL')
    se.navegar_url_chrome("https://www.nytimes.com/")
    log.debug('Check way to search news')
    if (search_by_url):
        seach_by_url()
    else:
        seach_by_webcontrols()
    filter_news()    
    data, columns = get_news()
    log.debug('Creating excel')
    df = create_dataframe(data, columns)
    dir_excel = dir_out + "/execution.xlsx"
    log.debug('Save excel')
    df.to_excel(dir_excel)
    log.debug('Finish')
    se.quit_driver_chrome()


main()
