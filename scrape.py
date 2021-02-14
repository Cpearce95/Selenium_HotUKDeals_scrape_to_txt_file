##Imports
import pandas as pd
import numpy as np
import os
import time as t
import requests
import lxml
import datetime
from datetime import *
import sys
from sys import argv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


start_time = datetime.now()
options = Options() ##Initializing selenium Options class for chrome driver options
##adding options for chrome driver
options.add_argument("--incognito") ##incognito to prevent cookies to device
options.add_argument("--disable-extensions") 
options.add_argument("--start-maximized")  ##Headless to avoid resource overhead
options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"]) ##disables pop-up ads     
    
##Function opens a txt file taking the user input {tag} to name the file
def create_file(tag):
    out_file = open(f"{tag}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt","w")
    return out_file


def scrape(tag, page_num,filename):
    titles,hrefs,shops,current_prices,orig_prices,images,disc_rates,dates = [],[],[],[],[],[],[],[] ##Initializing empty lists to hold scraped data
    driver = webdriver.Chrome('chromedriver.exe',options=options) ##initialise chrome driver passing in options
    url = fr'https://www.hotukdeals.com/tag/{tag}?page={page_num}' 
    driver.get(url)
    driver.implicitly_wait(1)
    soup = BeautifulSoup(driver.page_source,'lxml') ##Selenium passes page to bs4 to traverse the DOM
    articles = soup.find_all('article') ##Finds all of the article tags on the page.
    ##Loop through each article on the page and scrape data, appending into lists
    for article in articles: 
        try:
            title = article.find('a', class_='cept-tt').get('title')
            href = article.find('a', class_='cept-tt').get('href')
            shop = article.find('span', class_ = 'cept-merchant-name').get_text()
            current_price = article.find('span', class_ = 'thread-price').get_text()
            original_price = article.find('span', class_ = 'mute--text').get_text()
            image = article.find('img', class_ = 'thread-image').get('src')
            discount_rate = article.find('span', class_ = 'space--ml-1').get_text()
            
            titles.append(title)
            hrefs.append(href)
            shops.append(shop)
            current_prices.append(current_price)
            orig_prices.append(original_price)
            images.append(image)
            dates.append(str(datetime.now()))
            disc_rates.append(discount_rate)
        except:
            pass
    t.sleep(.5)
    driver.close()
    
    df = pd.DataFrame() ##Initialising dataframe to hold data
    d = {'title': titles, 'seller': shops, 'price_now': current_prices,
    'orig_price': orig_prices, 'discount_rate': disc_rates,'image_link':images,'product_link': hrefs, 'datetime': dates} ##Creating dict from now populated lists
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df.transpose()
    
    ##Clean the numerical data 
    df['discount_rate'] = df['discount_rate'].str.rstrip('% off')
    df['price_now'] = df['price_now'].map(lambda x: x.replace('£','')).map(lambda x: x.replace(',',''))
    df['orig_price'] = df['orig_price'].map(lambda x: x.replace('£','')).map(lambda x: x.replace(',',''))
    
    ##Convert to desired data types, more useful when target location is a database
    df['discount_rate'] = pd.to_numeric(df['discount_rate'])
    df['price_now'] = pd.to_numeric(df['price_now'])
    df['orig_price'] = pd.to_numeric(df['orig_price'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    ##Drop entire row dupes
    df = df.drop_duplicates()
    if page_num == 1:
        columns = ['title', 'seller', 'price_now', 'orig_price', 'discount_rate',
       'image_link', 'product_link', 'datetime']
        ##Write dataframe to text file
        df.to_csv(f"{filename}",sep='|',columns=columns,mode='a',encoding='utf-8',index=False)
    else:
        df.to_csv(f"{filename}",sep='|',header=None,mode='a',encoding='utf-8',index=False)
        
    
if int(argv[2]) <= 0:
    print("Please enter a positive number of pages to scrape i.e > 0.")
else:
    file = create_file(argv[1])
    print(f"{start_time}: Scraping {argv[1]} products from {argv[2]} page(s) of Hot Uk Deals.com")
    for page in range(1,int(argv[2]) + 1):
        print(page)
        scrape(argv[1],page,file.name)
    end_time = datetime.now()    
    print(f"{end_time}: Scraping completed in {end_time - start_time}")

