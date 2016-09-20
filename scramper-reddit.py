#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import json
import os.path
import time
import urllib.parse

import bs4
import praw
import requests


def scrape_urls_from_reddit(subreddit):
    r = praw.Reddit(user_agent='Test Script by /u/st3fan')
    r.login('', '', disable_warning=True)
    submissions = r.get_subreddit(subreddit).get_top(limit=50)
    for s in submissions:
        url = s.url
        if url.startswith("http://") or url.startswith("https://"):
            yield url


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


SUBREDDITS=["news", "worldnews", "AnythingGoesNews", "truereddit",
            "europe", "qualitynews", "neutralnews"]


if __name__ == "__main__":
    results = {}
    if os.path.isfile("results-reddit.json"):
        with open('results-reddit.json', 'r') as fp:
            results = json.load(fp)
    while True:
        for subreddit in SUBREDDITS:
            print("*** Spidering subreddit", subreddit)
            for url in scrape_urls_from_reddit(subreddit):
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
                        with open('results-reddit.json', 'w') as fp:
                            json.dump(results, fp, indent=4)
            time.sleep(60)
