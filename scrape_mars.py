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
    if "Hemisphere" not in title_str:  
        title_str = title_str.replace("Enhanced", "Hemisphere")
    else:
        pass
    title = title_str.split(",")

    # Query for Cerberus Hemisphere
    ## The daggum wayback website changed how it was feeding me pages 
    ## (by adding a pop-up banner), late at night. I had to redo this 
    ## section; i'm leaving in the old code in case it goes back to the
    ## old way.
    
    xpath = '//*[@id="product-section"]/div[2]/div[1]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    #browser.back()
    url_1 = browser.url
    browser.visit(url_1)
    response_1 = requests.get(url_1)
    soup1 = BeautifulSoup(response_1.text, 'html.parser')
    img_src = soup1.find("img", class_="wide-image")["src"]
    final_src = "http://web.archive.org" + img_src
    img_url.append(final_src) 
    browser.back()

    # xpath3 = '//*[@id="wm-expand"]/span[2]'
    # browser.find_by_xpath(xpath3).first.click()
    # time.sleep(1)
    # xpath4 = '//*[@id="wm-capresources"]/div/a'
    # browser.find_by_xpath(xpath4).first.click()
    # browser.back()
    # browser.back()

    # Query for Schiaparelli Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[2]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    #browser.back()
    url_1 = browser.url
    browser.visit(url_1)
    response_1 = requests.get(url_1)
    soup1 = BeautifulSoup(response_1.text, 'html.parser')
    img_src = soup1.find("img", class_="wide-image")["src"]
    final_src = "http://web.archive.org" + img_src
    img_url.append(final_src) 
    browser.back()
    
    # xpath3 = '//*[@id="wm-expand"]/span[2]'
    # browser.find_by_xpath(xpath3).first.click()
    # time.sleep(1)
    # xpath4 = '//*[@id="wm-capresources"]/div/a'
    # browser.find_by_xpath(xpath4).first.click()
    # browser.back()
    # browser.back()

    # Query for Syrtis Major Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[3]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)
    #browser.back()
    url_1 = browser.url
    browser.visit(url_1)
    response_1 = requests.get(url_1)
    soup1 = BeautifulSoup(response_1.text, 'html.parser')
    img_src = soup1.find("img", class_="wide-image")["src"]
    final_src = "http://web.archive.org" + img_src
    img_url.append(final_src) 
    browser.back()

    # xpath3 = '//*[@id="wm-expand"]/span[2]'
    # browser.find_by_xpath(xpath3).first.click()
    # time.sleep(1)
    # xpath4 = '//*[@id="wm-capresources"]/div/a'
    # browser.find_by_xpath(xpath4).first.click()
    # browser.back()
    # browser.back()

    # Query for Valles Marineris Hemisphere
    xpath = '//*[@id="product-section"]/div[2]/div[4]/div/a'
    browser.find_by_xpath(xpath).first.click()
    time.sleep(1)
    xpath2 = '//*[@id="wide-image"]/div/ul/li[1]/a'
    browser.find_by_xpath(xpath2).first.click()
    time.sleep(1)

    # xpath3 = '//*[@id="wm-expand"]/span[2]'
    # browser.find_by_xpath(xpath3).first_click()
    # time.sleep(1)
    # xpath4 = '//*[@id="wm-capresources"]/div/a'
    # time.sleep(1)

    url_1 = browser.url
    browser.visit(url_1)
    response_1 = requests.get(url_1)
    soup1 = BeautifulSoup(response_1.text, 'html.parser')
    img_src = soup1.find("img", class_="wide-image")["src"]
    final_src = "http://web.archive.org" + img_src
    img_url.append(final_src) 
    # browser.windows.current = browser.windows[4]
    # img_url.append(browser.url)
    # browser.windows.current = browser.windows[3]
    # img_url.append(browser.url)
    # browser.windows.current = browser.windows[2]
    # img_url.append(browser.url)
    # browser.windows.current = browser.windows[1]
    # img_url.append(browser.url)

    # Create dictionary to hold hemisphere data
    hemi_dict = {k: v for k, v in zip(title, img_url)}

    mars_hemi_images_dict = dict(zip(title, img_url))

    # Create dataframe to hold hemisphere data
    mars_hemi_df = pd.DataFrame(
    {'title': title,
     'img_url': img_url,
    })
    mars_hemi_df.set_index("title")

    mars_dict["mars_hemi_title"] = title
    mars_dict["mars_hemi_img_url"] = img_url
    mars_dict["mars_hemi_imgs"] = hemi_dict
    #mars_dict["mars_hemi_imgs_items"] = hemi_items

    return mars_dict
    #json.loads(mars_dict.to_json())
    browser.quit()
