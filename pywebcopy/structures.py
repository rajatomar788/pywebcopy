# -*- coding: utf-8 -*-

"""
aerwebcopy.structures
~~~~~~~~~~~~~~~~~~~~~

Data structures powering aerwebcopy.
"""

import os
import bs4


from pywebcopy.exceptions import ConnectError

try:
    import robotparser
    import urlparse
except ImportError:
    from urllib import robotparser
    from urllib import parse as urlparse


__all__ = [
    'RobotsTxt', 'WebPage'
]


__metaclass__ = type




class Url(object):
    """Provides several operations on a url."""

    def __init__(self, url):
        self.url = url
        self.is_valid = self.check_validity(self.url)

    def netloc(self):
        return utils.hostname(self.url)

    def port(self):
        return utils.url_port(self.url)

    def abs_url(self):
        """Returns a absolute url from any url."""

    @staticmethod
    def check_validity(url):
        """Checks if a url is valid."""


class RobotsTxt(robotparser.RobotFileParser, object):
    """ Represents the sites 'robots.txt' with some funcs """

    def __init__(self, robots_url=None):

        self.robots_url = robots_url or ''
        
        if self.robots_url is None or self.robots_url == '':
            self.is_dummy = True

        else:
            self.is_dummy = False    
            super(RobotsTxt, self).__init__()
            self.set_url(self.robots_url)
            try:
                self.read()
            except IOError:
                raise ConnectError("Connection Failed!")

    def __repr__(self):
        return '<RobotsTxt at {}>'.format(self.robots_url)

    def can_fetch(self, user_agent, url):
        """ Determines if user-agent can fetch the specific
        part of the website.
        """
        if self.is_dummy:
            return True

        super(RobotsTxt, self).can_fetch(user_agent, url)


from pywebcopy import utils
from pywebcopy import generators
from pywebcopy import core

class WebPage(bs4.BeautifulSoup):
    """ Represents a web page in python code.

    You can use any method of beautiful_soup and also
    save the web page with class methods easily

    :param url: url of the web page
    :param download_path: directory in which to save files

    Example:
    
        wp = WebPage(url='http://google.com', download_path='some/path')
        
        wp.save_html_only()
        wp.save_complete()

    """

    def __init__(self, url, download_path, parser='html5lib', *args, **kwargs):

        self.request = self._make_request(url)
        self.file_name = self._file_name(self.request.url)
        self.url = urlparse.urljoin(self.request.url, self.file_name).strip('/')
        self.file_path = generators.generate_path_for(self.url, create_path=False)
        self.download_path = download_path

        config = __import__('config')
        # set these values so that no error in other functions occur
        config.config['URL'] = self.url
        config.config['MIRRORS_DIR'] = self.download_path

        del config

        super(WebPage, self).__init__(self.request.content, parser=parser, *args, **kwargs)

    def __repr__(self):
        return '<WebPage {}>'.format(self.url)

    @staticmethod
    def _make_request(url):
        """ Makes the http request to the server """

        req = core.get(url)
        
        # check if request was successful
        if not req.ok:
            core.now('Server Responded with an error!', level=4, to_console=True)
            core.now('Error code: %s' % str(req.status_code), to_console=True)
            raise ConnectError("Error while fetching %s" % url)

        return req

    def _bytes_content(self):
        """ Returns a byte type content of the html page """

        # Resolves compatibility issues to bytes func on python2 and python3

        if py3:
            content = bytes(str(self), "utf-8")
        else:
            content = str(self)
        
        return content

    @staticmethod
    def _file_name(url):
        """ Returns filename from url or a default value """

        # file name if given e.g. file.html or file.asp else index.html
        if os.path.splitext(utils.url_path(url))[1] == '.com' or \
            os.path.splitext(utils.url_path(url))[1].find('.') == -1 or \
                url.endswith('/'):
            return 'index.html'

        else: 
            return ''

    def save_html_only(self):
        """ Saves only the html of the page """

        # directly save the file
        core.new_file(download_loc=self.file_path, content=self._bytes_content())

    def save_assets_only(self):
        """ Save any css or js or image used in html """

        # save any css or js or images linked to this page
        generators.generate_style_map(file_url=self.url, file_path=self.file_path, file_soup=self)

    def save_complete(self):
        """ Saves complete web page with html, css, js and images """

        # save any css or js or images linked to this page
        _final_content = generators.generate_style_map(file_url=self.url, file_path=self.file_path, file_soup=self)

        if py3:
            content = bytes(str(_final_content), "utf-8")
        else:
            content = bytes(str(_final_content))

        # finally save the html page itself
        _saved_file = core.new_file(download_loc=self.url, content=content)

        # parse any styles which are written in <style> tag of html file
        generators.extract_css_urls(url_of_file=self.url, file_path=_saved_file)
