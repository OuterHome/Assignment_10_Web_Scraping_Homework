# Import Dependencies
import time as time
import pandas as pd
import requests
import pymongo
import re
from collections import defaultdict
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup

# Define function for initializing the chrome browser
def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

# Define function for scraping Mars data and passing to dictionary for MongoDB
def scrape():
    browser = init_browser()

    # create mars dictionary to insert into a MongoDB
    mars_dict = {}

    # Set variables
    #html = browser.html
    #soup = BeautifulSoup(html, 'html.parser')

    ### Scrape Mars News ###
    url_news = 'https://mars.nasa.gov/news/'
    browser.visit(url_news)
    response_news = requests.get(url_news)

    # Create soup object from html
    soup = BeautifulSoup(response_news.text, 'html.parser')
    news_title = soup.find('div', class_="content_title").text
    news_p = soup.find('div', class_="rollover_description_inner").text

    # Add news data to mars_dict
    mars_dict["mars_headline"] = news_title
    mars_dict["news_paragraph"] = news_p

    ### Scrape Mars Image ###
    url_img = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_img)
    response_img = requests.get(url_img)

    # Create soup object from html
    soup = BeautifulSoup(response_img.text, 'html.parser')

    # Use splinter to navigate to the full image details page
    xpath = '//*[@id="full_image"]'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(2)
    xpath2 = '//*[@id="fancybox-lock"]/div/div[2]/div/div[1]/a[2]'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(2)
    xpath3 = '//*[@id="page"]/section[1]/div/article/figure/a/img'
    browser.find_by_xpath(xpath3).first.click()
    featured_image_url = browser.url

    # Add image url to mars_dict
    mars_dict["featured_mars_image"] = featured_image_url

    ### Scrape Mars Weather ###
    url_wx = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url_wx)
    response_wx = requests.get(url_wx)

    # Create soup object from html
    soup = BeautifulSoup(response_wx.text, 'html.parser')

    mars_weather_gather = soup.find\
    ('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text

    # Check whether tweet is about mars weather
    if "Sol" and "pressure" in soup.find\
    ('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text:
        mars_weather = mars_weather_gather
    else: 
        mars_weather = soup.find_next_sibling\
        ('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text

    # Add weather tweet to mars_dict
    mars_dict["mars_weather"] = mars_weather

    ### Scrape Mars Facts ###
    url_facts = 'http://space-facts.com/mars/'
    browser.visit(url_facts)
    response_facts = requests.get(url_facts)

    # Create soup object from html
    soup = BeautifulSoup(response_facts.text, 'html.parser')
    mars_facts = soup.find('table', id='tablepress-mars').text

    # Convert mars_facts into list
    mars_facts_list = mars_facts.split('\n\n\n')
    mars_facts_list = list(map(lambda mars_facts_list: mars_facts_list.strip(), mars_facts_list))
    mars_facts_list = [i.split(':') for i in mars_facts_list] 
    mars_facts_list.pop(0)
    mars_facts_list.pop(9)

    # Load table data into dataframe
    mars_facts_df = pd.DataFrame(data = mars_facts_list)
    mars_facts_df.columns = ["Criteria", "Facts"]
    mars_facts_df

    # Convert df to HTML table string
    mars_facts_html = mars_facts_df.to_html(escape=False)
    mars_facts_html

    # Add Mars facts to mars_dict
    mars_dict["mars_facts"] = mars_facts_html

    ### Scrape Mars Hemisphere images ###
    img_url = []
    title = []
    url_hemi = 'http://web.archive.org/web/20181114171728/https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
               
    browser.visit(url_hemi)
    response_hemi = requests.get(url_hemi)

    # Create soup object from html
    soup = BeautifulSoup(response_hemi.text, 'html.parser')
    result = soup.find_all('h3')

    # Prepare string
    title_str = str(result)
    title_str = title_str.replace("<h3>", "")
    title_str = title_str.replace("</h3>", "")
    title_str = title_str.replace("[", "")
    title_str = title_str.replace("]", "")
    title_str = title_str.strip()
    title_str = title_str.replace("Enhanced", "Hemisphere")
    title = title_str.split(",")

    # Query for Cerberus Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[1]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    img_url.append(browser.url)
    browser.back()

    # Query for Schiaparelli Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[2]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    img_url.append(browser.url)
    browser.back()

    # Query for Syrtis Major Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[3]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    img_url.append(browser.url)
    browser.back()

    # Query for Valles Marineris Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[4]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    img_url.append(browser.url)

    # Prepare title and img_url
    #title = ["title: " + s for s in title]
    #img_url = ["img_url: " + s for s in img_url]

    # Create dictionary to hold hemisphere data
    hemi_dict = {k: v for k, v in zip(title, img_url)}

    # Define function to split dictionary into 4 parts
    # def split_dict_equally(input_dict, chunks=4):
    #     return_list = [dict() for idx in range(chunks)]
    #     idx = 0
    #     for k,v in input_dict.items():
    #         return_list[idx][k] = v
    #         if idx < chunks-1:  # indexes start at 0
    #             idx += 1
    #         else:
    #             idx = 0
    #     return return_list

    # Split hemi_dict into a list of 4 dictionaries
    # split_dict_equally(hemi_dict, chunks=4)

    # Create hemisphere items
    #hemi_items = hemi_dict.items()

    # Add Mars hemisphere data to mars_dict
    ###mars_dict["mars_hemi_imgs"] = hemi_dict
    mars_dict_5 = {}
    mars_dict_5["title"] = title_str
    mars_dict_5["img_urg"] = img_url_str
    #mars_dict_list_5 = []
    #mars_dict_list_5.append(mars_dict_5.copy())
    #mars_dict_list_5
    mars_dict_6 = {k: v for k, v in zip(title, img_url)}
    mars_dict_6

    mars_dict["mars_hemi_imgs"] = mars_dict_6

    mars_dict["mars_hemi_title"] = title
    mars_dict["mars_hemi_img_url"] = img_url
    #mars_dict["report"] = build_report(mars_report)
    #mars_report = report.find_all("p")
    #mars_dict["mars_hemi_imgs_items"] = hemi_items

    return mars_dict
    #json.loads(mars_dict.to_json())
    browser.quit()

def build_report(mars_report):
    final_report = ""
    for p in mars_report:
        final_report += " " + p.get_text()
        print(final_report)
    return final_report
