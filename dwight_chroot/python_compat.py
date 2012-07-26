import platform

PY3 = (platform.python_version() >= '3')

if PY3:
    import urllib as urllib2
    from urllib.parse import urlsplit
    iteritems = dict.items
else:
    import urllib2
    from urlparse import urlsplit
    iteritems = dict.iteritems
