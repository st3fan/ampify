# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import urllib.parse

import ampify


def test_split_path():
    assert ampify.split_path("/") == ([""], None, None)
    assert ampify.split_path("/foo") == (["foo"], "foo", None)
    assert ampify.split_path("/foo.html") == (["foo.html"], "foo", "html")
    assert ampify.split_path("/foo.amp.html") == (["foo.amp.html"], "foo", "amp.html")
    assert ampify.split_path("/bar/foo") == (["bar", "foo"], "foo", None)
    assert ampify.split_path("/bar/foo.html") == (["bar", "foo.html"], "foo", "html")
    assert ampify.split_path("/bar/foo.amp.html") == (["bar", "foo.amp.html"], "foo", "amp.html")

def test_join_path():
    paths = [ "/", "/foo", "/foo/", "/foo.html", "/foo.amp.html",
              "/foo/bar", "/foo/bar/", "/foo/bar/baz.html", "/foo/bar/baz.amp.html" ]
    for path in paths:
        components, filename, extension = ampify.split_path(path)
        assert ampify.join_path(components, filename, extension) == path


def transformation_rules(old, new):
    return ampify.transformation_rules(urllib.parse.urlparse(old), urllib.parse.urlparse(new))

def test_change_hostname():
    rules = transformation_rules("http://www.example.com/article", "http://amp.example.com/article")
    assert rules == { "change-hostname": "amp.example.com" }

def test_prepend_path():
    rules = transformation_rules("http://www.example.com/article", "http://www.example.com/amp/article")
    assert rules == { "prepend-path": ["amp"] }

def test_append_path():
    rules = transformation_rules("http://www.example.com/article", "http://www.example.com/article/amp")
    assert rules == { "append-path": ["amp"] }

#def test_append_extension():
#    rules = transformation_rules("http://www.example.com/article", "http://www.example.com/article/amp")
#    assert rules == { "append-path": "/amp" }

def test_change_extension_nytimes():
    rules = transformation_rules("http://www.nytimes.com/2016/08/22/world/europe/blackpool-post-brexit-resort-town.html",
                      "http://mobile.nytimes.com/2016/08/22/world/europe/blackpool-post-brexit-resort-town.amp.html")
    assert rules == { "change-hostname": "mobile.nytimes.com", "change-extension": "amp.html" }

def test_append_filename():
    rules = transformation_rules("http://www.spiegel.de/international/business/volkswagen-how-officials-ignored-years-of-emissions-evidence-a-1108325.html",
                      "http://www.spiegel.de/international/business/volkswagen-how-officials-ignored-years-of-emissions-evidence-a-1108325-amp.html")
    assert rules == { "append-filename": "-amp" }



def test_transform_append_path():
    url = ampify.transform("http://www.example.com/article", { "append-path": ["amp"] })
    assert url == "http://www.example.com/article/amp"

def test_transform_append_filename():
    old = "http://www.spiegel.de/international/business/volkswagen-how-officials-ignored-years-of-emissions-evidence-a-1108325.html"
    new = "http://www.spiegel.de/international/business/volkswagen-how-officials-ignored-years-of-emissions-evidence-a-1108325-amp.html"
    assert ampify.transform(old, {"append-filename":"-amp"}) == new

def test_transform_change_extension():
    url = ampify.transform("http://www.nytimes.com/2016/08/22/world/europe/blackpool-post-brexit-resort-town.html",
                           { "change-hostname": "mobile.nytimes.com", "change-extension": "amp.html" })
    assert url == "http://mobile.nytimes.com/2016/08/22/world/europe/blackpool-post-brexit-resort-town.amp.html"
