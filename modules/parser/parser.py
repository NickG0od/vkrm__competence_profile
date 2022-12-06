import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import jellyfish
import re
import json


DRIVER_PATH = os.path.dirname(os.path.abspath(__file__)) + "/chromedriver.exe"
HH_URL = "https://hh.ru"
WAIT_TIMEOUT = 10
MAX_PAGES = 10
CONFIDENCE_FACTOR = 2


def init():
    os.system('cls') if os.name == "nt" else os.system('clear')
    print("Введите входные параметры для поиска:")
    print("-> Профессия, должность или компания (Оставьте поле пустым при необходимости)")
    proffesion = input()
    print("-> Уровень дохода (Оставьте поле пустым при необходимости)")
    salary = input()
    print("-> Регион (Оставьте поле пустым при необходимости)")
    region = input()
    status = start(proffesion, salary, region)
    return status


def start(proffesion, salary, region, pages_count=MAX_PAGES, full_search = False):
    if not pages_count or not isinstance(pages_count, int) or pages_count <= 0:
        pages_count = MAX_PAGES
    errors = []
    # PROXY_STR = "66.94.120.161:443" # https://sslproxies.org/
    options = webdriver.ChromeOptions()
    # options.add_argument(f"--proxy-server={PROXY_STR}")
    browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
    # browser.maximize_window()
    is_start_error = False
    try:
        browser.get(HH_URL)
        search_input = browser.find_element(By.ID, "a11y-search-input")
        search_input.click()
        search_input.send_keys(proffesion)
        search_input.send_keys(Keys.RETURN)
        wait_page_load(browser, By.ID, "a11y-search-input")
    except WebDriverException:
        is_start_error = True
        print(WebDriverException)
    if is_start_error:
        print("> Нажмите \"Enter\" для продолжения...")
        input()
        try:
            browser.get(HH_URL)
            search_input = browser.find_element(By.ID, "a11y-search-input")
            search_input.click()
            search_input.send_keys(proffesion)
            search_input.send_keys(Keys.RETURN)
            wait_page_load(browser, By.ID, "a11y-search-input")
        except WebDriverException:
            print(WebDriverException)
            errors.append(f"Ошибка при загрузке страницы. [{WebDriverException}]")
    if len(errors) > 0:
        browser.quit()
        return {'id': "", 'errors': errors}
    salary_str = ""
    if salary != "":
        salary_str = f"&salary={salary}"
    if region != "":
        try:
            elems = browser.find_elements(By.CSS_SELECTOR, "input.bloko-checkbox__input")
            for elem in elems:
                if elem.get_attribute("checked"):
                    elem.find_element(By.XPATH, "..").click()
                    break
            print(".. before")
            st = wait_page_load(browser, By.ID, "a11y-search-input")
            print(".. after/ ", st)
            elems = browser.find_elements(By.CSS_SELECTOR, ".bloko-link.bloko-link_pseudo")
            print(".. 1")
            for elem in elems:
                print('text: ', elem.text)
                if jellyfish.levenshtein_distance(elem.text, "Показать все") < CONFIDENCE_FACTOR:
                    elem.click()
            time.sleep(5)
            print(".. 2")
            input()
            region_input = browser.find_element(By.CSS_SELECTOR, ".bloko-input[placeholder='Поиск региона']")
            region_input.click()
            region_input.send_keys(region)
            region_input.send_keys(Keys.RETURN)
            time.sleep(3)
            print(".. 3")
            browser.find_element(By.CSS_SELECTOR, ".novafilters-list.novafilters-list_scrolling > li:nth-child(1) > label").click()
            wait_page_load(browser, By.ID, "a11y-search-input")
        except WebDriverException:
            print(WebDriverException)
            errors.append(f"Ошибка при обработки региона. [{WebDriverException}]")
    if len(errors) > 0:
        browser.quit()
        return {'id': "", 'errors': errors}
    found_elements = []
    c_url = browser.current_url
    c_page = 0
    flag = True
    try:
        add_to_url = f"{salary_str}&page=" if "area=" in c_url else f"?{salary_str}&page="
        while flag:
            time.sleep(1)
            print( f"{c_url}{add_to_url}{c_page}" )
            browser.get(f"{c_url}{add_to_url}{c_page}")
            wait_page_load(browser, By.ID, "a11y-search-input")
            tmp_elems = browser.find_elements(By.CSS_SELECTOR, ".vacancy-serp-item")
            if len(tmp_elems) > 0:
                for card in tmp_elems:
                    title = ""
                    link = ""
                    employer = ""
                    address = ""
                    salary = ""
                    description = ""
                    if find_element_handler(card, By.CSS_SELECTOR, "a.bloko-link:nth-child(1)") != None:
                        title = find_element_handler(card, By.CSS_SELECTOR, "a.bloko-link:nth-child(1)").text
                        link = find_element_handler(card, By.CSS_SELECTOR, "a.bloko-link:nth-child(1)").get_attribute("href")
                    if find_element_handler(card, By.CSS_SELECTOR, "div.vacancy-serp-item__meta-info-company") != None:
                        employer = find_element_handler(card, By.CSS_SELECTOR, "div.vacancy-serp-item__meta-info-company").text
                    if find_element_handler(card, By.CSS_SELECTOR, "div.bloko-text[data-qa='vacancy-serp__vacancy-address']") != None:
                        address = find_element_handler(card, By.CSS_SELECTOR, "div.bloko-text[data-qa='vacancy-serp__vacancy-address']").text
                    if find_element_handler(card, By.CSS_SELECTOR, "span[data-qa='vacancy-serp__vacancy-compensation']") != None:
                        salary = find_element_handler(card, By.CSS_SELECTOR, "span[data-qa='vacancy-serp__vacancy-compensation']").text
                        salary = salary.replace("\\u", "000 - ")
                        salary = salary.replace("f", "")
                    if find_element_handler(card, By.CSS_SELECTOR, "div.g-user-content") != None:
                        description = find_element_handler(card, By.CSS_SELECTOR, "div.g-user-content").text
                    if title != "" and link != "":
                        found_elements.append({"title": title, "link": link, "employer": employer, "address": address, "salary": salary, "description": description})
            else:
                flag = False
            c_page += 1
            if c_page > pages_count:
                flag = False
    except WebDriverException:
        print("> Ошибка при обработки карточек с объявлениями: ", WebDriverException)
        pass
    if len(found_elements) == 0:
        print("> Ничего не найдено по данному запросу")
        errors.append(f"Ничего не найдено по данному запросу")
        browser.quit()
        return {'id': "", 'errors': errors}
    # for element in found_elements:
    #     try:
    #         browser.get(element['link'])
    #         full_description = ""
    #         if find_element_handler(browser, By.CSS_SELECTOR, "div.vacancy-description") != None:
    #             full_description = find_element_handler(browser, By.CSS_SELECTOR, "div.vacancy-description").text
    #         element['full_description'] = full_description
    #     except WebDriverException:
    #         pass
    ts = int(time.time())
    folder_name = f"./data/{ts}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    json_string = json.dumps(found_elements, ensure_ascii=False)
    with open(f"{folder_name}/data.json", 'w', encoding='utf-8') as outfile:
        outfile.write(json_string)
    browser.quit()
    return {'id': ts, 'errors': errors}


def wait_page_load(browser, by_type, element):
    flag = False
    try:
        WebDriverWait(browser, WAIT_TIMEOUT).until(EC.presence_of_element_located((by_type, element)))
        flag = True
    except TimeoutException:
        pass
    return flag


def find_element_handler(parent, by_type, element):
    result = None
    try:
        result = parent.find_element(by_type, element)
    except WebDriverException:
        pass
    return result


if __name__ == "__main__":
    init()
