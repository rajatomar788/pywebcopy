# Copyright 2020; Raja Tomar
# See license for more details
import logging
import threading
import weakref

from requests import ConnectionError
from six import PY3
from six import string_types
from six.moves.urllib.parse import urlparse

from .elements import VoidResource
from .elements import CSSResource
from .elements import JSResource
from .elements import AbsoluteUrlResource
from .elements import GenericResource
from .elements import HTMLResource
from .elements import UrlRemover
from .helpers import RecentOrderedDict

logger = logging.getLogger(__name__)


class Index(RecentOrderedDict):
    """Files index dict.

    ..todo:: make it database synced
    """
    def __init__(self, *args, **kwargs):
        super(Index, self).__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def add_entry(self, k, v):
        with self.lock:
            self.__setitem__(k, v)

    def get_entry(self, k, default=None):
        return self.get(k, default=default)

    def add_resource(self, resource):
        location = resource.filepath
        self.add_entry(resource.context.url, location)
        if hasattr(resource.response, 'url'):
            self.add_entry(resource.response.url, location)
            if resource.response.history:
                for r in resource.response.history:
                    self.add_entry(r.url, location)

    index_resource = add_resource


class SchedulerBase(object):
    """A Synchronised resource processor.

    File paths would be based on the content-type header returned by the server
    but this would be slow because of being synchronous but is very reliable.
    """
    style_tags = frozenset(['link', 'style'])
    img_tags = frozenset(['img'])
    script_tags = frozenset(['script'])
    meta_tags = frozenset(['meta'])
    internal_tags = (style_tags | img_tags | script_tags | meta_tags)
    external_tags = frozenset(['a', 'form', 'iframe'])
    tags = (internal_tags | external_tags)

    def __init__(self, default=None, **data):
        self.data = dict()
        self.data.update(data)
        self.default = default
        self.index = Index()
        self.block_external_domains = True
        self.logger = logger.getChild(self.__class__.__name__)

    def set_default(self, default):
        self.default = default
        self.logger.info("Set the scheduler default as: [%r]" % default)

    def register_handler(self, key, value):
        self.data.__setitem__(key, value)
        self.logger.info(
            "Set the scheduler handler for %s as: [%r]" % (key, value))

    add_handler = register_handler

    def deregister_handler(self, key):
        self.data.__delitem__(key)
        self.logger.info("Removed the scheduler handler for: %s" % key)

    remove_handler = deregister_handler

    def get_handler(self, key, *args, **params):
        if key not in self.data:
            if self.default is None:
                raise KeyError(key)
            return self.default(*args, **params)
        else:
            return self.data[key](*args, **params)

    invalid_schemas = tuple([
        'data', 'javascript', 'mailto',
    ])

    def validate_url(self, url):
        if not isinstance(url, string_types):
            self.logger.error(
                "Expected string type, got %r" % url)
            return False
        scheme, host, port, path, query, frag = urlparse(url)
        if scheme in self.invalid_schemas:
            self.logger.error(
                "Invalid url schema: [%s] for url: [%s]"
                % (scheme, url))
            return False
        #: TODO: Add a user validation of the url before blocking
        return True

    def validate_resource(self, resource):
        if not isinstance(resource, GenericResource):
            self.logger.error(
                "Expected GenericResource, got %r" % resource)
            return False
        if isinstance(resource, VoidResource):
            self.logger.error(
                "Skipping VoidResource: %r" % resource)
            return False
        if not isinstance(resource.url, string_types):
            self.logger.error(
                "Expected url of string type, got %r" % resource.url)
            return False
        if isinstance(resource, HTMLResource) and self.block_external_domains:
            # FIXME: Change the algorithm to evaluate redirects.
            # print(resource.url, resource.context)
            if not resource.url.startswith(resource.context.base_url):
                self.logger.error(
                    "Blocked resource on external domain: %s" % resource.url)
                return False
        return self.validate_url(resource.url)

    def handle_resource(self, resource):
        indexed = self.index.get_entry(resource.url)
        if indexed:
            self.logger.debug(
                "[Cache] Resource Key: [%s] is available in the cache with value: [%s]"
                % (resource.url, indexed)
            )
            # modify the resources path resolution mechanism.
            return resource.__dict__.__setitem__('filepath', indexed)

        #: Update the index before doing any processing so that later calls
        #: in index finds this entry without going in infinite recursion
        #: Response could have been already present on disk
        self.index.add_entry(resource.context.url, resource.filepath)

        if self.validate_resource(resource):
            self.logger.debug("Processing valid resource: %r" % resource)
            return self._handle_resource(resource)
        self.logger.error("Discarding invalid resource: %r" % resource)

    def _handle_resource(self, resource):
        raise NotImplementedError()


class Collector(SchedulerBase):
    """A simple resource collector to use when debugging
    or requires manual collection of sub-files."""
    def __init__(self, *args, **kwargs):
        super(Collector, self).__init__(*args, **kwargs)
        self.children = list()

    def _handle_resource(self, resource):
        self.children.append(resource)


class Scheduler(SchedulerBase):
    def _handle_resource(self, resource):
        try:
            self.logger.debug('Scheduler trying to get resource at: [%s]' % resource.url)
            resource.get(resource.context.url)
            # NOTE :meth:`get` can change the :attr:`filepath` of the resource
            self.index.add_resource(resource)
        except ConnectionError:
            self.logger.error(
                "Scheduler ConnectionError Failed to retrieve resource from [%s]"
                % resource.url)
            # self.index.add_entry(resource.url, resource.filepath)
        except Exception as e:
            self.logger.exception(e)
            # self.index.add_entry(resource.url, resource.filepath)
        else:
            self.logger.debug('Scheduler running handler for: [%s]' % resource.url)
            resource.retrieve()
        self.index.add_resource(resource)


class ThreadingScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        super(ThreadingScheduler, self).__init__(*args, **kwargs)
        self.threads = weakref.WeakSet()
        self.timeout = None

    def __del__(self):
        self.close()

    def close(self, timeout=None):
        if not timeout:
            timeout = self.timeout
        threads = self.threads
        self.threads = None
        for thread in threads:
            if thread.is_alive() and thread is not threading.current_thread():
                thread.join(timeout)

    def _handle_resource(self, resource):
        def run(r):
            self.logger.debug('Scheduler trying to get resource at: [%s]' % r.url)
            # r.response = r.session.get(r.context.url)
            r.get(r.context.url)
            self.logger.debug('Scheduler running handler for: [%s]' % r.url)
            r.retrieve()
            return r.context.url, r.filepath
        thread = threading.Thread(target=run, args=(resource,))
        thread.start()
        self.threads.add(thread)


class GEventScheduler(Scheduler):
    def __init__(self, maxsize=None, *args, **kwargs):
        super(GEventScheduler, self).__init__(*args, **kwargs)
        try:
            from gevent.pool import Pool
        except ImportError:
            raise ImportError(
                "gevent module is not installed. "
                "Install it using pip: $ pip install gevent"
            )
        self.pool = Pool(maxsize)

    def __del__(self):
        self.close()

    def close(self, timeout=None):
        self.pool.kill(timeout=timeout)

    def _handle_resource(self, resource):
        def run(r):
            self.logger.debug('Scheduler trying to get resource at: [%s]' % resource.url)
            r.response = r.session.get(r.context.url)
            self.logger.debug('Scheduler running retrieving process: [%s]' % resource.url)
            r.retrieve()
            return r.context.url, r.filepath

        g = self.pool.spawn(run, resource)
        g.link_value(lambda gl: logger.info("Written the file from <%s> to <%s>" % gl.value))
        g.link_exception(lambda gl: logger.error(str(gl.exception)))


if PY3:
    class ThreadPoolScheduler(Scheduler):
        def __init__(self, maxsize=None, *args, **kwargs):
            super(ThreadPoolScheduler, self).__init__(*args, **kwargs)
            import concurrent.futures
            self.pool = concurrent.futures.ThreadPoolExecutor(maxsize)

        def __del__(self):
            self.close()

        def close(self, wait=None):
            self.pool.shutdown(wait)

        def _handle_resource(self, resource):
            def run(r):
                self.logger.debug('Scheduler trying to get resource at: [%s]' % resource.url)
                r.response = r.session.get(r.context.url)
                self.logger.debug('Scheduler running retrieving process: [%s]' % resource.url)
                r.retrieve()
                return r.context.url, r.filepath

            def callback(ret):
                if ret.exception():
                    self.logger.error(str(ret.exception()))
                else:
                    self.logger.info("Written the file from <%s> to <%s>" % ret.result())

            g = self.pool.submit(run, resource)
            g.add_done_callback(callback)

    def thread_pool_default_scheduler(maxsize=4):
        ans = ThreadPoolScheduler(maxsize=maxsize)
        fac = default_scheduler()
        ans.default = fac.default
        ans.data = fac.data
        del fac
        return ans

    def thread_pool_crawler_scheduler(maxsize=4):
        ans = thread_pool_default_scheduler(maxsize=maxsize)
        for k in ans.meta_tags:
            ans.register_handler(k, HTMLResource)
        for k in ans.external_tags:
            ans.register_handler(k, HTMLResource)
        return ans

else:
    class ThreadPoolScheduler(object):
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "Python 2 does not have `futures` modules, "
                "hence you should use any other scheduler link gevent.!"
            )

    def thread_pool_scheduler(maxsize=4):
        raise RuntimeError(
            "Python 2 does not have futures modules, "
            "hence you should use any other scheduler link gevent.!", maxsize
        )

    def thread_pool_crawler_scheduler(maxsize=4):
        raise RuntimeError(
            "Python 2 does not have futures modules, "
            "hence you should use any other scheduler link gevent.!", maxsize
        )


def default_scheduler():
    ans = Scheduler()
    ans.default = GenericResource
    for k in ans.style_tags:
        ans.register_handler(k, CSSResource)
    for k in ans.img_tags:
        ans.register_handler(k, GenericResource)
    for k in ans.script_tags:
        ans.register_handler(k, JSResource)
    for k in ans.meta_tags:
        ans.register_handler(k, GenericResource)
    for k in ans.external_tags:
        ans.register_handler(k, AbsoluteUrlResource)
    return ans


def no_js_scheduler():
    ans = default_scheduler()
    for k in ans.script_tags:
        ans.register_handler(k, UrlRemover)
    return ans


def crawler_scheduler():
    ans = default_scheduler()
    for k in ans.meta_tags:
        ans.register_handler(k, HTMLResource)
    for k in ans.external_tags:
        ans.register_handler(k, HTMLResource)
    return ans


def threading_default_scheduler(timeout=None):
    ans = ThreadingScheduler()
    ans.timeout = timeout
    fac = default_scheduler()
    ans.default = fac.default
    ans.data = fac.data
    del fac
    return ans


def threading_crawler_scheduler(timeout=None):
    ans = threading_default_scheduler()
    ans.timeout = timeout
    for k in ans.meta_tags:
        ans.register_handler(k, HTMLResource)
    for k in ans.external_tags:
        ans.register_handler(k, HTMLResource)
    return ans


def gevent_default_scheduler(maxsize=4):
    ans = GEventScheduler(maxsize=maxsize)
    fac = default_scheduler()
    ans.default = fac.default
    ans.data = fac.data
    del fac
    return ans


def gevent_crawler_scheduler():
    ans = gevent_default_scheduler()
    for k in ans.meta_tags:
        ans.register_handler(k, HTMLResource)
    for k in ans.external_tags:
        ans.register_handler(k, HTMLResource)
    return ans


def base64_scheduler():
    raise NotImplemented
