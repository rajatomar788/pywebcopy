# -*- coding: utf-8 -*-

"""
pywebcopy.apis
~~~~~~~~~~~~~~

The complete ease of access collection.

"""
from __future__ import print_function
from webbrowser import open_new_tab

from . import config
from .core import zip_project
from .crawler import Crawler
from .webpage import WebPage

__all__ = ['save_webpage', 'save_website']


def webpage():
    """Returns a freshly prepared WebPage object.
    """
    return WebPage()


def save_webpage(url, project_folder, html=None, project_name=None,
                 encoding=None, reset_config=False, **kwargs):
    """Easiest way to save any single webpage with images, css and js.

    usage::
        >>> from pywebcopy import save_webpage
        >>> url = 'http://some-url.com/some-page.html'
        >>> download_folder = '/home/users/me/downloads/pages/'
        >>> project_name = 'some-recognisable-name'
        >>> kwargs = {'bypass_robots':True}
        >>> save_webpage(url, download_folder, project_name, **kwargs)


    :param url: url of the web page to work with
    :type url: str
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None
    :param html: file like object or html if available
    :type html: str
    :param encoding: explicit encoding declaration for decoding html
    :type encoding: str
    :param reset_config: whether to reset the config after saving the web page; could be useful if
    you are saving different web pages which are located on different servers.
    :type reset_config: bool
    """

    #: Set up the global configuration
    config.setup_config(url, project_folder, project_name, **kwargs)

    #: Create a object of web page
    wp = webpage()
    wp.url = config['project_url']
    wp.path = config['project_folder']

    #: Remove the extra files downloading if requested
    if not config.get('load_css'):
        wp.deregister_tag_handler('link')
        wp.deregister_tag_handler('style')
    if not config.get('load_javascript'):
        wp.deregister_tag_handler('script')
    if not config.get('load_images'):
        wp.deregister_tag_handler('img')

    if html:
        #: only set url in manual mode because its internally
        #: set in the get() method
        wp.set_source(html, encoding)

    else:
        # print("Fetching page")
        wp.get(wp.url)
        # print("Page fetched")

    # If encoding is specified then change it otherwise a default encoding is
    # always internally set by the get() method
    if encoding:
        wp.encoding = encoding

    # Instruct it to save the complete page
    wp.save_complete()

    # Everything is done! Now archive the files and delete the folder afterwards.
    if config['zip_project_folder']:
        zip_project(config['join_timeout'])

    if reset_config:
        # reset the config so that it does not mess up any con-current calls to
        # the different web pages
        config.reset_config()

    open_new_tab(wp.utx.file_path)


def save_website(url, project_folder, project_name=None, **kwargs):
    """Easiest way to clone a complete website.

    You need a functioning url to be able to save it.
    Html can't be used to invoke this function.


     usage::
        >>> from pywebcopy import save_website

        >>> url = 'http://some-site.com/'
        >>> download_folder = '/home/users/me/downloads/website-clone/'
        >>> project_name = 'some-recognisable-name'

        >>> kwargs = {'bypass_robots':True}

        >>> save_website(url, download_folder, project_name, **kwargs)


    :param url: url of the web page to work with
    :type url: str
    :param project_folder: folder in which the files will be downloaded
    :type project_folder: str
    :param project_name: name of the project to distinguish it
    :type project_name: str | None


    """
    html = kwargs.pop('html', None)
    if html:
        raise TypeError(
            "Website mirroring is not possible from a html string."
            " Did you mean to use save_webpage() instead?"
        )

    config.setup_config(url, project_folder, project_name, **kwargs)

    #: Not assigning to a variable so that it would be easy for garbage
    #: collection
    c = Crawler()
    c.url = config['project_url']
    c.path = config['project_folder']

    #: Remove the extra files downloading if requested
    if not config.get('load_css'):
        c.deregister_tag_handler('link')
        c.deregister_tag_handler('style')
    if not config.get('load_javascript'):
        c.deregister_tag_handler('script')
    if not config.get('load_images'):
        c.deregister_tag_handler('img')

    c.run()
    path = getattr(c, 'file_path', '')
    del c
    #: This function will zip the files downloaded from the server
    #: and will block until it is done
    if config['zip_project_folder']:
        zip_project(config['join_timeout'])

    open_new_tab(path)
