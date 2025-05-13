# Copyright 2020; Raja Tomar
# See license for more details
import logging
import operator
import os

from .elements import WebElement
from .schedulers import crawler_scheduler
from .schedulers import default_scheduler
from .schedulers import threading_crawler_scheduler
from .schedulers import threading_default_scheduler

__all__ = ['WebPage', 'Crawler']

logger = logging.getLogger(__name__)


class WebPage(WebElement):
    """
    WebPage built upon HTMLResource element.
    It provides various utilities like form-filling,
    external response processing, getting list of links,
    dumping html and opening the html in the browser.
    """

    @classmethod
    def from_config(cls, config):
        """It creates a `WebPage` object from a set config object.
        Under the hood it checks whether the config is set or not,
        then it creates a `session` using the `config.create_session()` method.
        It then creates a `scheduler` based on whether the threading is enabled or not.
        It also defines a `context` object which stores the path metadata for this structure.
        """
        if config and not config.is_set():
            raise AttributeError("Configuration is not setup.")

        session = config.create_session()
        if config.get('threaded'):
            scheduler = threading_default_scheduler(
                timeout=config.get_thread_join_timeout())
        else:
            scheduler = default_scheduler()
        context = config.create_context()
        ans = cls(session, config, scheduler, context)
        # XXX: Check connection to the url here?
        return ans

    element_map = property(
        operator.attrgetter('scheduler.data'),
        doc="Registry of different handler for different tags."
    )

    def save_complete(self, pop=False):
        """Saves the complete html+assets on page to a file and
        also writes its linked files to the disk.

        Implements the combined logic of save_assets and save_html in
        compact form with checks and validation.
        """
        self.scheduler.handle_resource(self)
        if pop:
            self.open_in_browser()
        return self.filepath

    def open_in_browser(self):
        """Open the page in the default browser if it has been saved.

        You need to use the :meth:`~WebPage.save_complete` to make it work.
        """
        if not os.path.exists(self.filepath):
            self.logger.info(
                "Can't find the file to open in browser: %s" % self.filepath)
            return False

        self.logger.info(
            "Opening default browser with file: %s" % self.filepath)
        import webbrowser
        return webbrowser.open('file:///' + self.filepath)

    # handy shortcuts
    run = crawl = save_assets = save_complete


class Crawler(WebPage):
    @classmethod
    def from_config(cls, config):
        """
        It creates a `Crawler` object from a set config object.
        Under the hood it checks whether the config is set or not,
        then it creates a `session` using the `config.create_session()` method.
        It then creates a `scheduler` based on whether the threading is enabled or not.
        The scheduler is different from the `WebPage` objects scheduler due to its
        ability to process the anchor tags links to different pages.
        It also defines a `context` object which stores the path metadata for this structure.
        """
        if config and not config.is_set():
            raise AttributeError("Configuration is not setup.")

        session = config.create_session()
        if config.get('threaded'):
            scheduler = threading_crawler_scheduler(
                timeout=config.get_thread_join_timeout())
        else:
            scheduler = crawler_scheduler()
        context = config.create_context()
        ans = cls(session, config, scheduler, context)
        # XXX: Check connection to the url here?
        return ans
