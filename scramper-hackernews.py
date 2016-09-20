#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import urllib.parse
import json
import os
import time

import bs4
import requests


def scrape_urls_from_hackernews():
    url = "https://news.ycombinator.com/newest"
    for page_num in range(2):
        print("Looking at", url)
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        for link in soup.find_all("a", "storylink"):
            href = link.get("href")
            if href.startswith("http://") or href.startswith("https://"):
                yield href

        morelink = soup.find("a", "morelink")
        if not morelink:
            return
        url = "https://news.ycombinator.com/" + morelink.get("href")
        time.sleep(5)


def check_page_for_amp(url):
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    link = soup.find("link", {"rel": "amphtml"})
    if link:
        href = link.get("href")
        if href.startswith("/"):
            return urllib.parse.urljoin(url, href)
        else:
            return href


if __name__ == "__main__":
    results = {}
    if os.path.isfile("results-hackernews.json"):
        with open('results-hackernews.json', 'r') as fp:
            results = json.load(fp)

    while True:
        for url in scrape_urls_from_hackernews():
            if url not in results:
                try:
                    print("*** Checking ", url)
                    ampurl = check_page_for_amp(url)
                    print("+++ Got ", ampurl)
                    results[url] = ampurl
                except Exception as e:
                    print("--- Error", e)
                    results[url] = None
                finally:
                    with open('results-hackernews.json', 'w') as fp:
                        json.dump(results, fp, indent=4)
        time.sleep(60)
