# -*- coding: utf-8 -*-

"""
pywebcopy.apis
~~~~~~~~~~~~~~

The complete ease of access collection.

"""
from __future__ import print_function
from webbrowser import open_new_tab

from . import LOGGER, config
from .core import zip_project
from .crawler import Crawler
from .parsers import deregister_tag_handler
from .webpage import WebPage


def webpage():
    """Returns a freshly prepared WebPage object.
    """
    return WebPage()


def save_webpage(project_url, project_folder, html=None, project_name=None,
                 encoding=None, reset_config=False, **kwargs):
    """Easiest way to save any single webpage with images, css and js.

    usage::
        >>> from pywebcopy import save_webpage
        >>> url = 'http://some-url.com/some-page.html'
        >>> download_folder = '/home/users/me/downloads/pages/'
        >>> project_name = 'some-recognisable-name'
        >>> kwargs = {'bypass_robots':True}
        >>> save_webpage(url, download_folder, project_name, **kwargs)


    :param str project_url: url of the webpage to work with
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None
    :param html: file like object or html if available
    :param str encoding: explicit encoding declaration for decoding html
    :type encoding: str
    :param bool reset_config: whether to reset the config after saving the webpage; could be useful if
    you are saving different webpages which are located on different servers.
    """

    LOGGER.info("Starting copy of webpage at : %s" % project_url)
    html = html
    #: Set up the global configuration
    config.setup_config(project_url, project_folder, project_name, **kwargs)

    #: Remove the extra files downloading if requested
    if config.get('load_css', False):
        deregister_tag_handler('link')
        deregister_tag_handler('style')
    if config.get('load_javascript', False):
        deregister_tag_handler('script')
    if config.get('load_images', False):
        deregister_tag_handler('img')

    #: Create a object of webpage
    wp = webpage()

    if html:
        #: only set url in manual mode because its internally
        #: set in the get() method
        wp.set_source(html, encoding, project_url)

    else:
        print("Fetching page")
        wp.get(project_url)
        print("Page fetched")

    # If encoding is specified then change it otherwise a default encoding is
    # always internally set by the get() method
    if encoding:
        wp.encoding = encoding

    # Instruct it to save the complete page
    wp.save_complete()

    # Everything is done! Now archive the files and delete the folder afterwards.
    if config['zip_project_folder']:
        zip_project()

    if reset_config:
        # reset the config so that it does not mess up any con-current calls to
        # the different web pages
        config.reset_config()

    open_new_tab(wp.utx.file_path)


def save_website(url, project_folder, project_name=None, **kwargs):
    """Easiest way to clone a complete website.

    You need a functioning url to be able to save it.
    Html cann't be used to envoke this function.


     usage::
        >>> from pywebcopy import save_website

        >>> url = 'http://some-site.com/'
        >>> download_folder = '/home/users/me/downloads/website-clone/'
        >>> project_name = 'some-recognisable-name'

        >>> kwargs = {'bypass_robots':True}

        >>> save_website(url, download_folder, project_name, **kwargs)


    :type url: str
    :param url: url of the webpage to work with
    :type project_folder: str
    :param project_folder: folder in which the files will be downloaded
    :type project_name: str | None
    :param project_name: name of the project to distinguish it
    """
    html = kwargs.pop('html', None)
    if html:
        raise Exception("Website mirroring is not possible from a html string."
                        " Did you mean to use save_webpage() instead?")

    config.setup_config(url, project_folder, project_name, **kwargs)

    #: Remove the extra files downloading if requested
    if config.get('load_css', False):
        deregister_tag_handler('link')
        deregister_tag_handler('style')
    if config.get('load_javascript', False):
        deregister_tag_handler('script')
    if config.get('load_images', False):
        deregister_tag_handler('img')

    #: Not assigning to a variable so that it would be easy for garbage
    #: collection
    c = Crawler(url)
    c.run()
    path = c.file_path
    del c
    #: This function will zip the files downloaded from the server
    #: and will block until it is done
    if config['zip_project_folder']:
        zip_project()

    open_new_tab(path)

