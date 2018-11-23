# KMNR Ad Council Scraper
# Scrape the Ad Council Digital PSA library and download new PSAs
# Made by Trainee Shane Bodimer Nov 2018
# Python 3.7

# Requires Chrome Driver: http://chromedriver.chromium.org/downloads

import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

def simpleGet(url):
    return requests.get(url).text

def simplePost(url, payload):
    return requests.post(url, params=payload)

def siteLogin(driver, username, password):
    driver.get("https://www.psacentral.org/authenticate/login")
    driver.find_element_by_id("email").send_keys(username)
    driver.find_element_by_id ("password").send_keys(password)
    driver.find_element_by_class_name("LoginForm-submit").click()
    return driver

# Take driver to specified URL
def goToUrl(driver, url):
    driver.get(url)
    return driver

# Find download button with id and press download
def downloadAsset(driver, asset_id):
    selector = '//div[@data-campaign-asset-group-id="'+asset_id+'"]'
    asset = driver.find_element_by_xpath(selector)
    download_button = asset.find_element_by_class_name("DirectDownloadLink") 
    driver.execute_script("arguments[0].scrollIntoView();", download_button)
    driver.execute_script("arguments[0].click();", download_button)
    return driver

# Create array of radio ids from any URL
def getRadioReleases(url):
    ids = []
    recent_html = simpleGet(url)
    html = BeautifulSoup(recent_html, 'html.parser')
    # Select all divs to find all asset ids
    for p in html.select('div'):
        if p.has_attr('data-campaign-asset-group-id'):
            ids.append(p['data-campaign-asset-group-id'])
    return ids

if __name__ == "__main__":

    # URL to search
    # Searches for most recent radio releases in past 3 months
    search_url = "https://www.psacentral.org/search?s=0&q=&t=radio&l=english&rd=past-3-months&ma=all&ms=all"

    # Get the radio ids of recent releases
    print("Getting recently updated radio releases...")
    recent_ids = getRadioReleases(search_url)
    print(len(recent_ids), "total assets found")

    # Compare with history of downloaded campaigns
    history = open("history.txt").read().splitlines()
    new_assets = list(set(recent_ids) - set(history))
    print(len(new_assets),"new radio assets found")

    # Append new assets to history file
    with open("history.txt", 'a') as file:
        for n in new_assets:
            file.write(n+"\n")
    
    if len(new_assets) != 0:

        # Set download folder and allow multiple downloads
        chromeOptions = webdriver.ChromeOptions()
        downloads = "/Users/shane/Desktop/downloads"
        prefs = {"download.default_directory" : downloads, "profile.default_content_setting_values.automatic_downloads": 1}
        chromeOptions.add_experimental_option("prefs",prefs)

        # Setup Chrome driver
        path = "/usr/local/bin/chromedriver"
        driver = webdriver.Chrome(executable_path=path, options=chromeOptions) 

        # Authenticate with Ad Council 
        driver = siteLogin(driver, "sbqd2@mst.edu", "KMnr!Nov23!2018**")

        # Go to search results page
        driver = goToUrl(driver, search_url)

        # Download new assets
        for i, n in enumerate(new_assets):
            driver = downloadAsset(driver, n)
            print(i+1,"of",len(new_assets),"downloaded")
            sleep(3)
        
        # Quit browser
        driver.quit()
    
    print("Process completed!")