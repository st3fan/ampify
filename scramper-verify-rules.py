#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


#
# scamper-verify-rules.py ampify-rules.json [results...]
#

import urllib.parse

import ampify


def verify_rules(domain, urls, rules):
    success_count = 0

    for old, new in urls:
        amp = apply_rules(old, rules)
        if new == amp:
            success_count += 1
        # else:
        #     print("FAIL OLD", old)
        #     print("FAIL NEW", new)
        #     print("FAIL AMP", amp)

    return [domain, len(urls), float(success_count) / float(len(urls))]


if __name__ == "__main__":
    pass
