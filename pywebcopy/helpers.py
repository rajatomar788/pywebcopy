# Copyright 2020; Raja Tomar
# See license for more details
import time
import functools
import threading

from requests.compat import OrderedDict
from six import BytesIO
from six.moves.collections_abc import MutableMapping


class RecentOrderedDict(MutableMapping):
    """
    A custom variant of the OrderedDict that ensures that the object most
    recently inserted or retrieved from the dictionary is at the top of the
    dictionary enumeration.
    """

    def __init__(self, *args, **kwargs):
        self._data = OrderedDict(*args, **kwargs)

    def __setitem__(self, key, value):
        if key in self._data:
            del self._data[key]
        self._data[key] = value

    def __getitem__(self, key):
        value = self._data[key]
        del self._data[key]
        self._data[key] = value
        return value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, value):
        return self._data.__contains__(value)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()


class ConcurrentDelay(object):
    """
    Blocking waiter which calculates the delay irrespective of the
    waiting call rather than just waiting on the specified time.

    for example if time between two calls for delay are 10 seconds apart
    but the timeout is set for 1 second then the second call will not block
    but a successive third call will be blocked for 1 second before completing.
    """

    def __init__(self, timeout=1 / 10):
        self.timeout = None
        self.set_timeout(timeout)
        self.start_time = time.time()
        self._cond = threading.Condition()
        # self.logger = logger.getChild(self.__class__.__name__)

    def set_timeout(self, t):
        if not isinstance(t, (int, float)):
            raise ValueError("Expected int or float, got %r" % t)
        if t <= -1:
            raise ValueError("Delay cannot be smaller than 0")
        self.timeout = t

    def delay(self):
        """Delays until the timeout is completed"""
        with self._cond:
            current_time = time.time()
            diff_time = current_time - self.start_time
            # prevent none type values from waiting infinitely
            if isinstance(self.timeout, (int, float)) \
                    and not diff_time >= self.timeout:
                # self.logger.debug(
                # "Waiting on request for [%r] seconds!" % self.timeout)
                self._cond.wait(self.timeout - diff_time)
            self.start_time = current_time


def lru_cache(maxsize=255, timeout=None):
    """lru_cache(maxsize = 255, timeout = None) --> returns a decorator which
    returns an instance (a descriptor).

        Purpose         - This decorator factory will wrap a function / instance method
                            and will supply a caching mechanism to the function.
                            For every given input params it will store the result in a queue
                            of maxsize size, and will return a cached ret_val
                            if the same parameters are passed.

        Params          - maxsize - int, the cache size limit, anything added above that will delete
                            the first values entered (FIFO).
                            This size is per instance, thus 1000 instances with maxsize of 255,
                            will contain at max 255K elements.
                        - timeout - int / float / None, every n seconds the cache is deleted,
                            regardless of usage. If None - cache will never be refreshed.

        Notes           - If an instance method is wrapped, each instance will have it's own cache
                            and it's own timeout.
                        - The wrapped function will have a cache_clear variable inserted
                            into it and may be called to clear it's specific cache.
                        - The wrapped function will maintain the original function's
                            docstring and name (wraps)
                        - The type of the wrapped function will no longer be that of a function
                            but either an instance of _LRU_Cache_class or a functools.partial type.

        On Error        - No error handling is done, in case an exception is raised - it will permeate up.
    """

    class _LRU_Cache_class(object):
        # noinspection PyShadowingNames
        def __init__(self, input_func, max_size, timeout):
            self._input_func = input_func
            self._max_size = max_size
            self._timeout = timeout

            # This will store the cache for this function, format -
            # {caller1 : [OrderedDict1, last_refresh_time1], caller2 : [OrderedDict2, last_refresh_time2]}.
            #   In case of an instance method - the caller is the instance, in case called
            #   from a regular function - the caller is None.
            self._caches_dict = {}

        def cache_clear(self, caller=None):
            # Remove the cache for the caller, only if exists:
            if caller in self._caches_dict:
                del self._caches_dict[caller]
                self._caches_dict[caller] = [OrderedDict(), time.time()]

        def __get__(self, obj, obj_type):
            """ Called for instance methods """
            return_func = functools.partial(self._cache_wrapper, obj)
            return_func.cache_clear = functools.partial(self.cache_clear, obj)
            # Return the wrapped function and wraps it to maintain the docstring and
            # the name of the original function:
            return functools.wraps(self._input_func)(return_func)

        def __call__(self, *args, **kwargs):
            """ Called for regular functions """
            return self._cache_wrapper(None, *args, **kwargs)

        # Set the cache_clear function in the __call__ operator:
        __call__.cache_clear = cache_clear

        def _cache_wrapper(self, caller, *args, **kwargs):
            # Create a unique key including the types (in order to differentiate between 1 and '1'):
            kwargs_key = "".join(map(lambda x: str(x) + str(type(kwargs[x])) + str(kwargs[x]), sorted(kwargs)))
            key = "".join(map(lambda x: str(type(x)) + str(x), args)) + kwargs_key

            # Check if caller exists, if not create one:
            if caller not in self._caches_dict:
                self._caches_dict[caller] = [OrderedDict(), time.time()]
            else:
                # Validate in case the refresh time has passed:
                if self._timeout is not None:
                    if time.time() - self._caches_dict[caller][1] > self._timeout:
                        self.cache_clear(caller)

            # Check if the key exists, if so - return it:
            cur_caller_cache_dict = self._caches_dict[caller][0]
            if key in cur_caller_cache_dict:
                return cur_caller_cache_dict[key]

            # Validate we didn't exceed the max_size:
            if len(cur_caller_cache_dict) >= self._max_size:
                # Delete the first item in the dict:
                cur_caller_cache_dict.popitem(False)

            # Call the function and store the data in the cache (call it with
            # the caller in case it's an instance function - Ternary condition):
            cur_caller_cache_dict[key] = self._input_func(
                caller, *args, **kwargs) if caller is not None else self._input_func(
                *args, **kwargs
            )
            return cur_caller_cache_dict[key]

    # Return the decorator wrapping the class (also wraps the instance to
    # maintain the docstring and the name of the original function):
    return lambda input_func: functools.wraps(input_func)(_LRU_Cache_class(input_func, maxsize, timeout))


_missing = object()


class cached_property(property):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: A subclass of python's builtin property
    # decorator, we override __get__ to check for a cached value. If one
    # chooses to invoke __get__ by hand the property will still work as
    # expected because the lookup logic is replicated in __get__ for
    # manual invocation.

    # noinspection PyMissingConstructor
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, *args, **kwargs):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


class CallbackFileWrapper(object):
    """
    Small wrapper around a fp object which will tee everything read into a
    buffer, and when that file is closed it will execute a callback with the
    contents of that buffer.

    All attributes are proxied to the underlying file object.

    This class uses members with a double underscore (__) leading prefix so as
    not to accidentally shadow an attribute.
    """

    def __init__(self, fp, callback=None):
        self.__buf = BytesIO()
        self.__fp = fp
        self.__callback = callback
        self.__once_done = False

    def __getattr__(self, name):
        # The vagaries of garbage collection means that self.__fp is
        # not always set.  By using __getattribute__ and the private
        # name[0] allows looking up the attribute value and raising an
        # AttributeError when it doesn't exist. This stop things from
        # infinitely recurring calls to getattr in the case where
        # self.__fp hasn't been set.
        #
        # [0] https://docs.python.org/2/reference/expressions.html#atom-identifiers
        fp = self.__getattribute__("_CallbackFileWrapper__fp")
        return getattr(fp, name)

    def __is_fp_closed(self):
        try:
            return self.__fp.fp is None

        except AttributeError:
            pass

        try:
            return self.__fp.closed

        except AttributeError:
            pass

        return False

    def close(self):
        if self.__callback:
            # self.__callback(self.__buf.getvalue())
            self.__callback()

        # We assign this to None here, because otherwise we can get into
        # really tricky problems where the CPython interpreter dead locks
        # because the callback is holding a reference to something which
        # has a __del__ method. Setting this to None breaks the cycle
        # and allows the garbage collector to do it's thing normally.
        self.__callback = None
        self.__once_done = True
        return self.__getattribute__("_CallbackFileWrapper__fp").close()

    def rewind(self):
        if self.__once_done:
            self.__fp.close()
            self.__fp = self.__buf
            self.__buf = BytesIO()
            self.__fp.seek(0)
            self.__once_done = False

    def read(self, amt=None):
        data = self.__fp.read(amt)
        self.__buf.write(data)
        if self.__is_fp_closed():
            self.close()
        return data

    def _safe_read(self, amt):
        data = self.__fp._safe_read(amt)
        if amt == 2 and data == b"\r\n":
            # urllib executes this read to toss the CRLF at the end
            # of the chunk.
            return data

        self.__buf.write(data)
        if self.__is_fp_closed():
            self.close()
        return data


class RewindableResponse(object):
    """
    Used by :class:`WebPage` to store current resource
    content to minimize the number of requests made while
    working with a page.
    """
    def __init__(self, fp):
        self.fp = fp
        self.buffer = BytesIO()
        self.once_done = threading.Event()

    def __getattr__(self, name):
        fp = self.__getattribute__("fp")
        return getattr(fp, name)

    @classmethod
    def from_response(cls, response):
        ans = cls(response.raw)
        return ans

    def read(self, n=None):
        if self.fp.closed:
            self.once_done.set()
        data = self.fp.read(n)
        self.buffer.write(data)
        if self.fp.closed:
            self.once_done.set()
        return data

    def rewind(self):
        if not self.once_done.is_set():
            return False
        self.fp.close()
        self.buffer.seek(0)
        self.fp = self.buffer
        self.buffer = BytesIO()
