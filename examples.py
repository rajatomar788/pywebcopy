# -*- coding: utf-8 -*-

"""
Tutorials for sample use-cases with pywebcopy.

This modules demos some general use cases when
working with pywebcopy.

You can uncomment the functions which you like and modify
its arguments to instantly get the results.
"""


import os
import time
import platform


if platform.system() == 'Windows':
    try:  # Python 3.3+
        preferred_clock = time.perf_counter
    except AttributeError:  # Earlier than Python 3.
        preferred_clock = time.clock
else:
    preferred_clock = time.time

start = preferred_clock()


# Import the library
import pywebcopy
'''
If you are getting `pywebcopy.exceptions.AccessError` Exception.
then check if website allows scraping of its content.

or

Uncomment the line below.
'''
# pywebcopy.config['bypass_robots'] = True


"""
If you want to overwrite existing files in the directory then
use the over_write config key.

or 

Uncomment the line below.
"""
# pywebcopy.config['over_write'] = True


"""
If you want to change the project name.
use the project_name config key.

or 

Uncomment the line below.
"""
# pywebcopy.config['project_name'] = 'my_project'


"""
Save Single Webpage

Particular webpage can be saved easily using the following 
methods.

For `pywebcopy.exceptions.AccessError` use the code provided on top sections.

choose and uncomment the method which you like to use.
"""

# method 1 Best practice 

from pywebcopy import WebPage
from pywebcopy import config


def scrape(url, folder, timeout=1):
  
    config.setup_config(url, folder)

    wp = WebPage()
    wp.get(url)

    # start the saving process
    wp.save_complete()

    # join the sub threads
    for t in wp._threads:
        if t.is_alive():
           t.join(timeout)

    # location of the html file written 
    return wp.file_path


# method 2
'''
pywebcopy.save_webpage('http://www.google.com', project_folder='c://Saved_Webpages/',)
'''

# method 3 using local html
'''
page_url = 'http://localhost:5000/'
handle = open(os.path.join(os.getcwd(), 'tests', 'test.html'), 'rb')
download_folder = os.path.join(os.path.dirname(os.getcwd()), 'saved')
pywebcopy.save_webpage(page_url, download_folder, html=handle, bypass_robots=True)

'''

'''
Whole Websites

Use caution when copying websites as this can overload or damage the
servers of the site and rarely could be illegal, so check everything before
you proceed.


choose method and uncomment the method which you like.
'''


# method 1:  Best Practise

from pywebcopy import Crawler
from pywebcopy import config


def crawl(url, folder, timeout=1):
  
    config.setup_config(url, folder)

    cr = Crawler()
    cr.get(url)

    # start the saving process
    cr.crawl()

    # join the sub threads
    for t in cr._threads:
        if t.is_alive():
           t.join(timeout)

    # location of the html file written 
    return cr.file_path


# method 2: Using simple method
'''
pywebcopy.save_website(page_url, download_folder)
'''

print("Execution time : ", preferred_clock() - start)
