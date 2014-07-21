from __future__ import absolute_import

import json
import socket

from six import text_type
from tornado import ioloop, httpclient, httpserver, httputil

from .. import bases, compat


class TornadoMixin(object):

    """Test tornado applications with AAA testing.

    Mix this class in over :class:`test_helpers.bases.BaseTest` or
    similar classmethod-based testing class and you can directly
    test tornado-based applications.

    **Usage**

    .. code-block:: python

       from unittest import TestCase
       from test_helpers import mixins
       import myproject

       class WhenMyApplicationsGets(mixins.TornadoMixin, TestCase):

           @classmethod
           def setUpClass(cls):
               super(WhenMyApplicationGets, cls).setUpClass()
               cls.start_tornado(myproject.Application())
               cls.execute()

           @classmethod
           def tearDownClass(cls):
               super(WhenMyApplicationGets, cls).tearDownClass()
               cls.stop_tornado()

           @classmethod
           def execute(cls):
               cls.response = cls.get('/index')

           def should_return_ok(self):
               self.assertEqual(self.response.code, 200)

    **Attributes**

    This mix-in creates three useful attributes in addition to the
    methods.  Each of the attributes is initialized by :meth:`start_tornado`
    and will be :data:`None` until that method is called.

    .. attribute:: client

       The :class:`tornado.httpclient.HTTPClient` instance used to
       interact with the application.

    .. attribute:: io_loop

       The :class:`tornado.ioloop.IOLoop` instance that the application
       is attached to.

    .. attribute:: url_root

       The URL root used to interact with the application.  This refers
       to host and port that :attr:`io_loop` is attached to.

    .. attribute:: request_timeout

       The number of seconds to run the IO loop for before giving up
       on the request.

    """

    client = None
    io_loop = None
    request_timeout = 20.0
    url_root = None
    _result = None
    _request_timeout_failure = object()

    @classmethod
    def start_tornado(cls, application):
        """Start up tornado and register `application`.

        :param application: anything suitable as a Tornado *request
            callback* (see :class:`tornado.httpserver.HTTPServer`)

        This method binds a socket to an arbitrary temporary port,
        creates a new Tornado IOLoop, and adds the `application`'
        to it.  Calling any of the request-related methods will
        start the IOLoop and run it until a response is received.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        for port in range(32000, 32768):
            try:
                sock.setblocking(0)
                sock.bind(('127.0.0.1', port))
                sock.listen(128)
                break
            except IOError:
                pass
        else:
            raise RuntimeError('failed to find open port')

        cls.url_root = 'http://{0}:{1}'.format(*sock.getsockname())
        cls.io_loop = ioloop.IOLoop()
        cls.io_loop.make_current()

        cls.client = httpclient.AsyncHTTPClient(io_loop=cls.io_loop)
        cls.server = httpserver.HTTPServer(application, cls.io_loop)
        cls.server.add_socket(sock)

    @classmethod
    def stop_tornado(cls):
        """Terminate the tornado IO loop."""
        cls.io_loop.clear_current()
        cls.io_loop.close(all_fds=True)

    @classmethod
    def delete(cls, path, **kwargs):
        """Issue a ``DELETE`` request."""
        return cls.request('DELETE', path, **kwargs)

    @classmethod
    def get(cls, path, **kwargs):
        """Issue a ``GET`` request."""
        return cls.request('GET', path, **kwargs)

    @classmethod
    def post(cls, path, body, **kwargs):
        """Issue a ``POST`` request."""
        return cls.request('POST', path, body=body, **kwargs)

    @classmethod
    def put(cls, path, body, **kwargs):
        """Issue a ``PUT`` request."""
        return cls.request('PUT', path, body=body, **kwargs)

    @classmethod
    def request(cls, method, path, **kwargs):
        """Issue a request to the application.

        :param str method: HTTP method to invoke
        :param str path: possibly absolute path of the resource
            to invoke
        :param kwargs: additional arguments passed to the
            :class:`tornado.httpclient.HTTPRequest` initializer

        :returns: either a :class:`tornado.httpclient.HTTPResponse`
            instance or :data:`None` if the request timed out.

        The `path` parameter can be a relative path or an absolute
        URL.  It will be joined to :attr:`url_root` before the
        request object is created.

        """
        request = httpclient.HTTPRequest(
            compat.urljoin(cls.url_root, path), method=method, **kwargs)
        cls.client.fetch(request, callback=cls._on_request_complete)
        return cls._wait_for_completion()

    @classmethod
    def _on_request_complete(cls, result, **_):
        """Called when a request completes or times out.

        :param result: the response received from the application
            or :data:`._request_timeout_failure`

        """
        cls._result = result
        cls.io_loop.stop()

    @classmethod
    def _wait_for_completion(cls):
        def timeout():
            try:
                raise RuntimeError('timeout failure')
            finally:
                cls._on_request_complete(cls._request_timeout_failure)

        tmo_handle = cls.io_loop.add_timeout(
            cls.io_loop.time() + cls.request_timeout, timeout)
        cls.io_loop.start()
        cls.io_loop.remove_timeout(tmo_handle)

        assert cls._result is not cls._request_timeout_failure
        return cls._result


class TornadoTest(TornadoMixin, bases.BaseTest):

    """Tornado version of :class:`~.bases.BaseTest`.

    This class acts as a replacement for :class:`~.bases.BaseTest`
    with the Tornado magic pre-mixed.  All that you have to do
    is:

    1. set :attr:`tornado_application` as a top-level class
       attribute *OR*
    2. pass the ``application`` keyword to :meth:`configure`
       and make sure that this class is the first one in the
       ``__mro__``

    In either case, the ``application`` is the Tornado *request
    callback* that is being tested.  See
    :class:`tornado.httpserver.HTTPServer` for a complete
    description of what constitutes a *"request callback"*.

    """

    tornado_application = None
    """The Tornado request handler callable."""

    @classmethod
    def configure(cls, application=None):
        """Configures the Tornado IOLoop.

        :param application: overrides :attr:`tornado_application`

        """
        cls.start_tornado(application or cls.tornado_application)
        super(TornadoTest, cls).configure()

    @classmethod
    def annihilate(cls):
        """Terminates the Tornado application."""
        super(TornadoTest, cls).annihilate()
        cls.stop_tornado()
