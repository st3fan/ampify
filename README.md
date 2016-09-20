AMPify
=

*Stefan Arentz, August 2016*

__Experiment, Hack, Unstable__

This is a WebExtension experiment that makes the browser prefer AMP content. Before a page load the extension will try to recognize the URL and see if it can be transformed in a URL that points to the AMP content of the same page.

It does this with a fixed set of rules (in `rules.json`) that was generated with the Python scripts in this repository.

Developed on Firefox 48. May work on other browsers. I don't know the WebExtensions API very well and although this works, there are a number of bad things happening. For example the original URL still appears in your history and 404s are not handled super well.
