#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://daltonmatos.com'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
TRANSLATION_FEED_ATOM = 'feeds/all-%s.atom.xml'
LANG_EN_FEED_ATOM = TRANSLATION_FEED_ATOM % "en"

CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'


DELETE_OUTPUT_DIRECTORY = True

STATIC_PATHS = ['extra/favicon.png',
                'extra/CNAME',
                'extra/robots.txt',
                'extra/elf-add-symbol.cpp',
                'extra/extract-symbols-metadata.py',
                'extra/elf-add-symbol-v2.cpp',
                'extra/extract-symbols-metadata-v2.py',
                ]
EXTRA_PATH_METADATA = {
    'extra/CNAME': {
        'path': 'CNAME'
    },
    'extra/favicon.png': {
        'path': 'favicon.png'
    },
    'extra/robots.txt': {
        'path': 'robots.txt'
    },
    'extra/elf-add-symbol.cpp': {
        'path': 'elf-add-symbol.cpp'
    },
    'extra/extract-symbols-metadata.py': {
        'path': 'extract-symbols-metadata.py'
    },
    'extra/elf-add-symbol-v2.cpp': {
        'path': 'elf-add-symbol-v2.cpp'
    },
    'extra/extract-symbols-metadata-v2.py': {
        'path': 'extract-symbols-metadata-v2.py'
    },
}

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
GOOGLE_ANALYTICS = "UA-61818194-1"

FEED_ATOM = 'feeds/atom.xml'
