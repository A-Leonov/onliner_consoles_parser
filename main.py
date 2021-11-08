"""Requires chromedriver for your OS and Chrome versions"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import json
import random


def get_links(url):  # getting links of consoles

    cat_url = url + "?page="    # urls to iterate through all pages

    options = Options()
    options.page_load_strategy = 'eager'    # to prevent endless first page loading
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        time.sleep(1)
        catalogue = driver.find_element(By.XPATH,   # to create cookies and load amount of shop items
                                        '/html/body/div[1]/div/div/div/header/div[2]/div/nav/ul[1]/li[1]/a[2]/span')
        catalogue.click()
        time.sleep(3)
        driver.back()   # same as previous

        soup = BeautifulSoup(driver.page_source, 'lxml')
        pages = str(soup.find_all("a", class_="schema-pagination__pages-link")[-1])    # finding amount of pages
        pages = pages.split('>')[1].split('<')[0]
        pages = int(pages)

        urls = []

        for i in range(1, pages + 1):

            driver.get(cat_url + f'{i}')
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'lxml')
            divs = soup.find_all("div", class_="schema-product__title")    # getting divs with titles and links

            for item in divs:
                item_url = item.find("a").get("href")    # getting links from anchor tags
                urls.append(item_url)

            time.sleep(random.randint(3, 5))

        with open("item_urls.txt", "a") as file:    # writing links in a file
            for url in urls:
                file.write(f'{url}\n')

    except Exception as _ex:
        print(_ex)

    finally:
        driver.close()
        driver.quit()


def collect_data():
    with open("item_urls.txt", "r") as file:    # reading links from the file
        urls = [url.strip() for url in file]    # strip is for removing \n symbols
        result_list = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        try:

            item_name = soup.find("h1", class_="catalog-masthead__title").text.strip().split('приставка')[-1].strip()
            try:
                price = soup.find("a", class_="offers-description__link offers-description__link_nodecor").text.strip()
            except:
                price = 'None'
            try:
                capacity = soup.find(text="""
                Объем накопителя
                                    """).findNext('td').text.split()    # yes, this is right format to parse Onliner's tables
                capacity = ' '.join([value.strip() for value in capacity])
            except:
                capacity = 'None'

            try:
                resolution = soup.find(text="""
                Максимальное разрешение в играх
                                    """).findNext('td').text.split()
                resolution = ' '.join([value.strip() for value in resolution])
            except:
                resolution = 'None'

            print(item_name, price, capacity, resolution)
            result_list.append(
                {'url': url,
                 'name': item_name,
                 'price': price,
                 'capacity': capacity,
                 'resolution': resolution
                 })

        except Exception as _ex:
            print(_ex)

    with open('result_list.json', 'a') as file:    # dumping our list to a json file
        json.dump(result_list, file, indent=4, ensure_ascii=False)



def main():
    get_links('https://catalog.onliner.by/console')
    collect_data()


if __name__ == "__main__":
    main()
