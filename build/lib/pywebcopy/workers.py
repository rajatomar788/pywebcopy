# -*- coding: utf-8 -*-

"""
pywebcopy.workers
~~~~~~~~~~~~~~~~~

Provides different services to several modules in pywebcopy.

"""

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from . import utils, LOGGER
from .generators import AssetsGenerator
from .core import zip_project, new_file, get
from .config import config
from .exceptions import InvalidUrlError
from .parsers import parse, parse_content
from .parsers import WebPage as WebPageParser
from .urls import Url


def save_webpage(project_url, project_folder, project_name=None, html=None, encoding=None, method=None, reset_config=False, **kwargs):
    """ Easiest way to save any single webpage.

    HTML type is not supported in fancy other generators hence if html is provided
    then it will fall back to default regardless of the method specified.

    :param project_url: url of the webpage to work with
    :param project_name: friendly name to easily recogonise this project
    :param project_folder: folder in which store all the downloaded files
    :param method: method used for saving the webpage; if you don't know then leave it as is
    :param reset_config: whether to reset the config after saving the webpage; could be useful if
    you are saving different webpages which are located on different servers.
    """

    if not html and method == 'generator':
        req = get(project_url)

        if req is None or not req.ok:
            raise InvalidUrlError("Provided Url didn't work! Url: %s" % project_url)

        config.setup_config(req.url, project_folder, project_name, **kwargs)

        soup = parse_content(req.content, parser='html5lib')

        url_obj = Url(req.url)
        url_obj.default_filename = 'index.html'
        url_obj.base_path = config['project_folder']
        wp = AssetsGenerator(soup, url_obj)
        wp.generate_style_map()

        # Now save the actual html markup
        new_file(url_obj.file_path, None, wp.soup.encode(encoding='iso-8859-1', formatter='html5'))
    else:
        # Default fallback; Probably best available
        WebPageParser(project_url, project_folder, project_name, encoding=encoding, HTML=html, **kwargs).save_complete()

    # Everything is done! Now archive the files and delete the folder afterwards.
    zip_project()

    if reset_config:
        # reset the config so that it does not mess up any con-current calls to
        # the different web pages
        config.reset_config()

    # ALL DONE
    LOGGER.info("Downloaded Contents Size :: %s KB's" % str(config['download_size'] // 1024))


class WebPage(AssetsGenerator):
    """Extends functionality of _Webpage and AssetsGenerator Classes in
    single Class object.
    """

    def __init__(self, url, project_folder, project_name=None, **kwargs):

        config.setup_config(url, project_folder, project_name or utils.hostname(url), **kwargs)

        self.http_request = get(url, stream=True)

        if not self.http_request or not self.http_request.ok:
            raise InvalidUrlError("Provided url didn't work %s" % url)

        self.url_obj = Url(self.http_request.url)
        self.url_obj.default_filename = 'index.html'
        self.url_obj._unique_fn_required = False
        self.url_obj.base_path = config['project_folder']

        super(WebPage, self).__init__(parse_content(self.http_request.content, config['parser']), self.url_obj)

    def save_complete_using_generator(self):
        """Saves complete webpage with css, js or images etc."""

        # Basically scans and saves any css or js or image it finds and replaces the correct location
        # in the parsed html content
        self.generate_style_map()

        # Extracts any css url defined in <style> tag of html file and also encodes the content
        # in the specified encoding which should be suitable to display any languages charset
        _contents = self.extract_css_urls(contents=self.soup.encode(encoding="ISO-8859-1",
                                                                    formatter="html5"), url_obj=self.url_obj)

        # Just regular save of file by using its contents and saving to disk
        new_file(self.url_obj.file_path(), None, _contents)


class Crawler(object):
    """Crawls a specific url and saves any internal pages found. """

    def __init__(self, base_page_url, project_config=None, scan_level=2):
        self.config = project_config or config
        self.base_page_url = base_page_url
        self.crawled_urls = list()
        self.crawlable_urls = list()
        self.scan_level = scan_level

    def crawl(self, _url=None, level=0):
        """ Scans pages for links to other pages to save in COPY_WHOLE_WEBSITE mode.

        fetches the first page and scans for links to
        other pages which are under your given _url
        """

        if not _url:
            _url = self.base_page_url

        LOGGER.info("Crawling the webpage at %s" % _url)

        # save first page first, then proceed
        try:
            wp = WebPage(_url, self.config['project_folder'], self.config['project_name'])
        except InvalidUrlError as e:
            LOGGER.error(e)
            return

        wp.save_complete()

        LOGGER.debug("Webpage saved at location %s" % wp.url_obj.file_path())

        # if max deep level is reached
        if level == self.scan_level:
            LOGGER.warning("Crawler reached max deep level! Returning..")
            return

        # select all the links on page
        a_tags = wp.bs4.find_all('a', href=True)

        LOGGER.debug("Found %d links on this webpage." % len(a_tags))

        del wp

        # add internal links to valid links to the future crawlable links
        for i in a_tags:

            _link = urljoin(_url, i.get('href', ''))

            if _link.startswith(self.base_page_url) and _link not in self.crawlable_urls:
                self.crawlable_urls.append(_link)

        del a_tags

        # every _url found will be checked and sent to be saved through the
        # save_webpage method
        for _url in self.crawlable_urls:

            # if _url is already saved
            if _url in self.crawled_urls:
                # go to the next _url
                continue

            LOGGER.info("Sending _url for next deep level search %s" % _url)
            # send this _url again for _url searching
            self.crawl(_url, level=(level + 1))
            self.crawled_urls.append(_url)


def save_website(url, project_folder, project_name, **kwargs):
    """Saves the complete website with one function."""

    config.setup_config(url, project_folder, project_name, **kwargs)
    crawler = Crawler(url)
    crawler.crawl()
