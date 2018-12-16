#!/usr/bin/env python3

import requests
import os

from bs4 import BeautifulSoup
from sys import argv

# search results of all english radio programming from the past 3 months
SEARCH_URL = "https://www.psacentral.org/search?s=&q=&t=radio&l=english&rd=past-3-months&ma=all&ms=all"

# base URL for requesting campaign JSON objects
API_URL = "https://www.psacentral.org/api/group?id={}"


class Asset:
    def __init__(self, url, title, length, format):
        self.url = url
        self.title = title
        self.length = length
        self.format = format

        self.filename = f"{title} {length}.{format}"


def main(download_location):
    campaign_ids = get_campaign_ids(SEARCH_URL)
    assets = get_assets(campaign_ids)
    download_assets(assets, download_location)


# get unique ID for each campaign
def get_campaign_ids(url):
    campaign_ids = []

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    for campaign in soup.find_all("div", class_="GroupPromo"):
        campaign_ids.append(campaign["data-campaign-asset-group-id"])

    return campaign_ids


# fetch asset information and return list of Asset objects
def get_assets(campaign_ids):
    assets = []

    for id in campaign_ids:
        # get JSON object
        r = requests.get(API_URL.format(id))

        # loop over assets
        for a in r.json():
            # only english assets
            if a["language"] == "English":
                # dumb additional condition to prevent downloading assets for US territories
                if "Market Specific" in a["title"] and (not a["marketArea"] or "MO" not in a["marketArea"]):
                    continue

                # create asset object, striping leading colon from length and making format lowercase
                assets.append(Asset(a["sourceUrl"], a["title"], a["length"][1:], a["fileFormat"].lower()))

    return assets


# download assets to specified location
def download_assets(assets, download_location):
    for asset in assets:
        path = os.path.join(download_location, asset.title)

        # if the directory doesn't exist, create it
        if not os.path.exists(path):
            os.mkdir(path)

        # get asset data
        r = requests.get(asset.url)

        # write MP3 data to file
        with open(os.path.join(path, asset.filename), "wb") as f:
            f.write(r.content)


if __name__ == "__main__":
    main(argv[1])
