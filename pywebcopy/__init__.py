"""
    ____       _       __     __    ______                     _____
   / __ \__  _| |     / /__  / /_  / ____/___  ____  __  __   /__  /
  / /_/ / / / / | /| / / _ \/ __ \/ /   / __ \/ __ \/ / / /     / /
 / ____/ /_/ /| |/ |/ /  __/ /_/ / /___/ /_/ / /_/ / /_/ /     / /
/_/    \__, / |__/|__/\___/_.___/\____/\____/ .___/\__, /     /_/
      /____/                               /_/    /____/

PyWebCopy is a free tool for copying full or partial websites locally
onto your hard-disk for offline viewing.

PyWebCopy will scan the specified website and download its content onto your hard-disk.
Links to resources such as style-sheets, images, and other pages in the website
will automatically be remapped to match the local path.
Using its extensive configuration you can define which parts of a website will be copied and how.

What can PyWebCopy do?
PyWebCopy will examine the HTML mark-up of a website and attempt to discover all linked resources
such as other pages, images, videos, file downloads - anything and everything.
It will download all of theses resources, and continue to search for more.
In this manner, WebCopy can "crawl" an entire website and download everything it sees
in an effort to create a reasonable facsimile of the source website.

What can PyWebCopy not do?
PyWebCopy does not include a virtual DOM or any form of JavaScript parsing.
If a website makes heavy use of JavaScript to operate, it is unlikely PyWebCopy will be able
to make a true copy if it is unable to discover all of the website due to
JavaScript being used to dynamically generate links.

PyWebCopy does not download the raw source code of a web site,
it can only download what the HTTP server returns.
While it will do its best to create an offline copy of a website,
advanced data driven websites may not work as expected once they have been copied.


# Copyright 2020; Raja Tomar
# See license for more details
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

..todo::
    *1. Fix parser breaks on empty string.
    *2. Fix WebPage links and files method emptying the response stream.
    *3. Fix meta element in the head of the WebPage.
    *4. Add threading flag in the cmd and api.
    *5. Fix the MultiParser should be sub class of GenericElement.
    6. Fix Asynchronous http requests for the sub elements.
    7. Fix infinite nesting of anchor links requests on a single element.
    *8. Fix concurrent delay b/w requests to be domain specific.
"""

import logging
import warnings

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ['save_website', 'save_webpage']


def save_page(url,
              project_folder=None,
              project_name=None,
              bypass_robots=None,
              debug=False,
              open_in_browser=True,
              delay=None,
              threaded=None,):
    """Easiest way to save any single webpage with images, css and js.

    example::

        from pywebcopy import save_webpage
        save_webpage(
            url="https://httpbin.org/",
            project_folder="E://savedpages//",
            project_name="my_site",
            bypass_robots=True,
            debug=True,
            open_in_browser=True,
            delay=None,
            threaded=False,
        )

    :param url: url of the web page to work with
    :type url: str
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None
    :param bypass_robots: whether to follow the robots.txt rules or not
    :param debug: whether to print deep logs or not.
    :param open_in_browser: whether or not to open a new tab after saving the webpage.
    :type open_in_browser: bool
    :param delay: amount of delay between two concurrent requests to a same server.
    :param threaded: whether to use threading or not (it can break some site).
    """
    from .configs import get_config
    config = get_config(url, project_folder, project_name, bypass_robots, debug, delay, threaded)
    page = config.create_page()
    page.get(url)
    if threaded:
        warnings.warn(
            "Opening in browser is not supported when threading is enabled!")
        open_in_browser = False
    page.save_complete(pop=open_in_browser)


save_web_page = save_webpage = save_page


def save_website(url,
                 project_folder=None,
                 project_name=None,
                 bypass_robots=None,
                 debug=False,
                 open_in_browser=False,
                 delay=None,
                 threaded=None):
    """Crawls the entire website for html, images, css and js.

    example::

        from pywebcopy import save_website
        save_website(
            url="https://httpbin.org/",
            project_folder="E://savedpages//",
            project_name="my_site",
            bypass_robots=True,
            debug=False,
            open_in_browser=True,
            delay=None,
            threaded=False,
        )

    :param url: url of the web page to work with
    :type url: str
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None
    :param bypass_robots: whether to follow the robots.txt rules or not
    :param debug: whether to print deep logs or not.
    :param open_in_browser: whether or not to open a new tab after saving the webpage.
    :type open_in_browser: bool
    :param delay: amount of delay between two concurrent requests to a same server.
    :param threaded: whether to use threading or not (it can break some site).
    """
    from .configs import get_config
    config = get_config(url, project_folder, project_name, bypass_robots, debug, delay, threaded)
    crawler = config.create_crawler()
    crawler.get(url)
    if threaded:
        warnings.warn(
            "Opening in browser is not supported when threading is enabled!")
        open_in_browser = False
    crawler.save_complete(pop=open_in_browser)
