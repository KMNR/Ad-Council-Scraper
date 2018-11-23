# KMNR-AdCouncilScraper

Scrape new PSAs from the Ad Council website

## Requirements

- Python 3.7
- [Beautiful Soup](https://pypi.org/project/beautifulsoup4/)
- [Selenium](https://pypi.org/project/selenium/)
- [Google Chrome Driver](http://chromedriver.chromium.org/)

## How it works

`scrape.py` queries the Ad Council website for newly released radio productions by visiting this search url: [psacentral.org/search?s=0&...](https://www.psacentral.org/search?s=0&q=&t=radio&l=english&rd=past-3-months&ma=all&ms=all). It creates a list of recent asset IDs and compares it to previously downloaded asset IDs.

New assets are downloaded using Selenium and the ChromeDriver.

## Installation

Instructions are for MacOS Mojave

1. Clone the project

   `git clone https://github.com/shanebodimer/KMNR-AdCouncilScraper.git`

2. Install the needed dependencies for Python 3.7

   `pip3 install beautifulsoup4`

   `pip3 install selenium`

3. Install ChromeDriver from http://chromedriver.chromium.org/

4. Find the path of your Chrome driver:

   `which chromedriver`

   Make sure that the path in `scrape.py` matches your path

5. Run `python3.7 scrape.py`
