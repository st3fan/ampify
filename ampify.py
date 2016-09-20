# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import urllib.parse


#
# Returns:
#  ([""], None) for /
#  (["a", "b.html"], "b", "html") for /a/b.html
#  (["a", "b"], None) for /a/b
#  (["a", "b", ""], None) for /a/b/
#

def split_path(path):
    assert path # None or "" are invalid paths
    components = path.split("/")[1:]
    if components:
        if components[-1]:
            filename = components[-1].split(".", 1)
            if len(filename) == 2:
                return components, filename[0], filename[1]
            else:
                return components, filename[0], None
    return components, None, None


def join_path(components, filename, extension):
    components = [""] + components # Because split_path removed the first empty element
    if components[-1]:
        path = "/".join(components[0:-1])
        if filename:
            path += "/" + filename
            if extension:
                path += "." + extension
        return path
    else:
        return "/".join(components)


def transform_filename(old_filename, new_filename):
    if old_filename != new_filename:
        # foo.html -> amp-foo.html
        if new_filename.endswith(old_filename):
            return {"prepend-filename": new_filename[len(new_filename)-len(old_filename)]}
        # foo -> foo-amp
        if new_filename.startswith(old_filename):
            return {"append-filename": new_filename[len(old_filename):]}


def transform_extension(old_ext, new_ext):
    if old_ext != new_ext:
        return {"change-extension": new_ext}


def transform_path(old_path, new_path):
    if old_path != new_path:
        if new_path.endswith(old_path) or new_path.startswith(old_path):
            if new_path.endswith(old_path):
                path = new_path[:len(new_path)-len(old_path)]
                return {"prepend-path": path.split("/")[1:]}
            if new_path.startswith(old_path):
                path = new_path[len(old_path):]
                return {"append-path": path.split("/")[1:]}


#
# Returns { "change-hostname": "amp.foo.com", ...}
#

def transformation_rules(old, new):
    transformations = {}

    old_path, old_filename, old_ext = split_path(old.path)
    new_path, new_filename, new_ext = split_path(new.path)

    if old.hostname != new.hostname:
        transformations["change-hostname"] = new.hostname

    if old.scheme != new.scheme:
        transformations["change-protocol"] = new.scheme

    if old.query and not new.query:
        transformations["clear-query"] = True
    elif new.query:
        transformations["set-query"] = new.query

    path_transformations = transform_path(old.path, new.path)
    if path_transformations:
        transformations.update(path_transformations)

    extension_transformations = transform_extension(old_ext, new_ext)
    if extension_transformations:
        transformations.update(extension_transformations)

    filename_transformations = transform_filename(old_filename, new_filename)
    if filename_transformations:
        transformations.update(filename_transformations)

    if not transformations:
        return None

    return transformations


def transform(url, rules):
    url = list(urllib.parse.urlsplit(url))

    path, filename, ext = split_path(url[2])

    print("PATH", path)
    print("FILENAME", filename)
    print("EXT", ext)

    if "change-protocol" in rules:
        url[0] = rules["change-protocol"]
    if "change-hostname" in rules:
        url[1] = rules["change-hostname"]
    if "prepend-path" in rules:
        path = rules["prepend-path"] + path
    if "append-path" in rules:
        path = path + rules["append-path"]
    if "set-query" in rules:
        url[3] = rules["set-query"]
    if "clear-query" in rules:
        url[3] = None

    if "change-extension" in rules:
        ext = rules["change-extension"]

    if "prepend-filename" in rules:
        filename = rules["prepend-filename"] + filename

    if "append-filename" in rules:
        filename = filename + rules["append-filename"]

    url[2] = join_path(path, filename, ext)
    print("NEW URL", url[2])

    return urllib.parse.urlunsplit(url)
