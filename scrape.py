#!/usr/bin/env python3

import requests
import os

from bs4 import BeautifulSoup
from shutil import rmtree
from sys import argv

# list of campaigns
BROWSE_URL = "https://www.psacentral.org/browse-campaigns"

# base URL for requesting campaign JSON objects
API_URL = "https://www.psacentral.org/api/group?id="

# list of campaigns that we don't want to download
BLACKLIST = [
    "https://www.psacentral.org/campaign/emergency-preparedness-nyc"
]


class Campaign:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Asset:
    def __init__(self, campaign, url, title, length, format):
        self.campaign = campaign
        self.url = url
        self.title = title
        self.length = length
        self.format = format

        self.filename = f"{title} {length}.{format}"


def main(download_location):
    campaigns = get_campaigns(BROWSE_URL)
    assets = get_assets(campaigns)
    clear_dir(download_location) # clear download location
    download_assets(assets, download_location) # download assets to download location


# fetch campaign information and return list of Campaign objects
def get_campaigns(url):
    # get HTML of campaign list and parse
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # find all campaign links
    campaign_links = []
    for tag in soup.find_all("div", class_="CampaignPromo-media"):
        link = tag.a["href"]

        # prevent duplicates and blacklisted campaigns from being added
        if link not in campaign_links and link not in BLACKLIST:
            campaign_links.append(tag.a["href"])

    campaigns = []
    for link in campaign_links:
        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")

        # find all campaign IDs and names
        for tag in soup.find_all("div", class_="GroupPromo"):
            # only radio campaigns
            if tag["data-type"] == "Radio":
                campaign = Campaign(tag["data-campaign-asset-group-id"], tag["data-campaign-name"])
                campaigns.append(campaign)

    return campaigns


# fetch asset information and return list of Asset objects
def get_assets(campaigns):
    assets = []

    for campaign in campaigns:
        # get JSON object
        r = requests.get(API_URL + campaign.id)

        # loop over assets
        for a in r.json():
            # only english assets
            if a["language"] == "English":
                # prevent downloading market specific assets if market area is not specified or not MO
                if "Market Specific" in a["title"] and (not a["marketArea"] or "MO" not in a["marketArea"]):
                    continue

                # create asset object, stripping leading colon from length and making format lowercase
                asset = Asset(campaign, a["sourceUrl"], a["title"], a["length"][1:], a["fileFormat"].lower())
                assets.append(asset)

    return assets


# clear all files and folders out of the specified path (USE WITH CARE)
def clear_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            rmtree(file_path)


# download assets to specified location
def download_assets(assets, download_location):
    for asset in assets:
        path = os.path.join(download_location, asset.campaign.name)

        # if the directory doesn't exist, create it
        if not os.path.exists(path):
            os.mkdir(path)

        # get asset audio
        r = requests.get(asset.url)

        # write audio data to file
        with open(os.path.join(path, asset.filename), "wb") as f:
            f.write(r.content)


if __name__ == "__main__":
    main(argv[1])
