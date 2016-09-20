#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


#
# scamper-results-to-rules.py results.json ...
#


import collections
import json
import os
import pprint
import urllib.parse
import sys

from ampify import transformation_rules


def path_to_regex(path):
    regex = "^"
    parts = path.split("/")[1:]
    for part in parts:
        if part == "":
            regex += '\/'
        if part.isdigit():
            regex += '\/([0-9]+)'
        else:
            regex += '\/([^/]+)'
    regex += "$"
    return regex


def path_to_regex2(path):
    regex = ""
    parts = path.split("/")[1:]
    for part in parts:
        if part == "":
            regex += '/'
        elif part.isdigit():
            regex += '/([0-9]+)'
        else:
            regex += '/([^/]+)'
    return regex


#
# Returns { "^/../$": {...transformations...}, "^/../$": {...transformations..} }
#

def build_rules(urls):
    rules = {} # { "^//$": {}, "^//$": {} }

    for url in urls:
        old, new = urllib.parse.urlparse(url[0]), urllib.parse.urlparse(url[1])
        transformations = transformation_rules(old, new)

        if not transformations:
            print("UNABLE TO BUILD TRANSFORMATIONS FOR", file=sys.stderr)
            print("OLD PATH: ", url[0], file=sys.stderr)
            print("NEW PATH: ", url[1], file=sys.stderr)
            print("", file=sys.stderr)
            next

        if path in rules:
            if rules[path] != transformations:
                print("DUPE PATH WITH DIFFERENT RULES", x, file=sys.stderr)
                print(rules[path], file=sys.stderr)
                print(transformations, file=sys.stderr)
                print("", file=sys.stderr)

        if transformations:
            path_regex = path_to_regex2(old.path)
            rules[path_regex] = transformations

    return rules


if __name__ == "__main__":
    results = {}
    for path in sys.argv[1:]:
        with open(path, 'r') as fp:
            results.update(json.load(fp))

    if False:
        for url, ampurl in results.items():
            if url and ampurl:
                u = urllib.parse.urlparse(url)
                print(" PATH:", u.path)
                print("REGEX:", path_to_regex2(u.path))
                print("")
        sys.exit(0)


    # Group all urls by scheme://domain
    scheme_domains = collections.defaultdict(list)
    for url, ampurl in results.items():
        if url and ampurl:
            u = urllib.parse.urlparse(url)
            scheme_domains[u.scheme + "://" + u.hostname].append((url, ampurl))

    #json.dump(scheme_domains, sys.stdout, indent=4)
    #sys.exit(1)

    # Build the rules
    all_rules = {}
    for scheme_domain,urls in scheme_domains.items():
        rules = build_rules(urls)
        if rules:
            all_rules[scheme_domain] = rules
    #print(len(all_rules))
    json.dump(all_rules, sys.stdout, indent=4)
