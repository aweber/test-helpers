import collections
import socket
import urllib
import uuid

from tornado import httpserver, httputil, web


class ServiceLayer(object):
    """
    Represents any number of HTTP services.

    Create an instance of this class to represent HTTP services that
    your application uses.  The underlying machinery will attach to
    the IOLoop that a :class:`tornado.testing.AsyncTestCase` provides
    so that it will respond to HTTP requests that you application makes.

    You create "endpoints" in the service layer by calling the
    :meth:`.add_endpoint` method.  This is required to set up the
    internal ``RequestHandler`` instance that will respond to
    application requests.  The independent "services" are isolated
    by using different listening ports (e.g., virtual hosts).  The
    :meth:`.get_service_url` method will return a full URL that will
    send requests to a specified service.

    You control each service's responses by calling :meth:`.add_response`
    for each expected request.  The response is matched to the incoming
    request using the HTTP method and request path for the service endpoint.
    Each response is returned in the order that it was added.

    """

    def __init__(self):
        super(ServiceLayer, self).__init__()
        self._application = _ServiceApplication(self)
        self._server = httpserver.HTTPServer(self._application)
        self._services = {}
        self._responses = collections.defaultdict(list)

    def add_endpoint(self, service, resource):
        """
        Register a new endpoint for a service.

        :param str service: name that you assign to this service
        :param str resource: resource path to make available for ``service``

        """
        if service not in self._services:
            new_service = _Service()
            self._services[service] = new_service
            self._server.add_socket(new_service.acceptor)
        self._application.add_endpoint(resource)

    def get_service_host(self, service):
        """Get the ``Host`` string for a registered service."""
        return self._services[service].host

    def get_service_url(self, service, *path, **query):
        """
        Build a URL that targets `service`.

        :param str service: name assigned to a registered service
        :param path: optional path to request
        :param query: optional parameters to pass in the query

        :return: URL that will be routed to `service`

        """
        base_url = 'http://{0}'.format(self.get_service_host(service))
        url = urllib.basejoin(base_url,
                              '/'.join(urllib.quote(segment, safe='')
                                       for segment in path))
        if query:
            url = '{0}?{1}'.format(url, urllib.urlencode(query))
        return url

    def add_response(self, service, request, response):
        """
        Register a response.

        :param str service: the service to attach the response to
        :param Request request: request that will trigger the response
        :param Response response: response to associate with request

        """
        self._services[service].add_response(request, response)

    def get_next_response(self, tornado_request):
        """
        Retrieve the next response that matches `tornado_request`

        :param tornado.httputil.HTTPServerRequest tornado_request:
            incoming request to match to a response

        :return: the appropriate :class:`Response` object
        :raises: :class:`AssertionError` when the request cannot be
            matched to a response

        """
        request = Request.from_tornado_request(tornado_request)
        for service in self._services.values():
            if service.host == tornado_request.headers['Host']:
                try:
                    return service.get_next_response(request)
                except IndexError:
                    break
        raise AssertionError('unexpected tornado_request', tornado_request)


class Request(object):
    """
    Represents a client request.

    :param str method: HTTP method of the request
    :param path: positional parameters that are joined together to form
        the requested path
    :param query: keyword parameters represent any query parameters

    Instances of this class are used bundle up the information about
    a specific request instead of passing a bunch of parameters.

    """

    def __init__(self, method, *path, **query):
        self.method = method
        self.path = list(path)

        self.resource = '/'.join(urllib.quote(segment, safe='')
                                 for segment in path)
        if not self.resource.startswith('/'):
            self.resource = '/{0}'.format(self.resource)

        self.query = query.copy()
        if self.query:
            normalized = sorted(self.query.items())
            self.url = '{0}?{1}'.format(self.resource,
                                        urllib.urlencode(normalized))
        else:
            self.url = self.resource

    @classmethod
    def from_tornado_request(cls, tornado_request):
        """
        Create a request instance from a tornado request.

        :param tornado.httputil.HTTPServerRequest tornado_request:
            the request to wrap

        This method makes it really easy to wrap ``self.request`` inside
        of a :class:`tornado.web.RequestHandler` instance.

        """
        return cls(tornado_request.method,
                   *tornado_request.path.split('/'),
                   **tornado_request.query_arguments)


class Response(object):
    """
    Represents a server's response.

    :param int status: the HTTP status code
    :param str reason: optional reason phrase.  If this is not
        provided, then the string ``'Unspecified'`` is used.
    :param bytes body: optional response body
    :param dict headers: optional response headers

    """

    def __init__(self, status, reason=None, body=None, headers=None):
        self.status = status
        self.reason = reason or 'Unspecified'
        self.body = body
        self.headers = httputil.HTTPHeaders(headers or {})


class _RecordingHandler(web.RequestHandler):

    def initialize(self):
        self._request_token = self.application.store_request(self)
        super(_RecordingHandler, self).initialize()

    def on_finish(self):
        self.application.store_response(self._request_token, self)
        super(_RecordingHandler, self).on_finish()


class _ProgrammableHandler(web.RequestHandler):

    def _do_request(self, *args, **kwargs):
        response = self.application.get_next_response(self)
        for name, value in response.headers:
            self.set_header(name, value)
        self.set_status(response.status, response.reason)
        if response.body:
            self.write(response.body)
        self.finish()

    delete = _do_request
    get = _do_request
    head = _do_request
    options = _do_request
    patch = _do_request
    post = _do_request
    put = _do_request


class _ServiceHandler(_RecordingHandler, _ProgrammableHandler):
    pass


class _ServiceApplication(web.Application):

    def __init__(self, service_layer):
        super(_ServiceApplication, self).__init__()
        self.request_history = collections.defaultdict(list)
        self.responses = collections.defaultdict(list)
        self.service_layer = service_layer
        self._known_endpoints = set()

    def store_request(self, handler):
        return uuid.uuid4().hex

    def add_endpoint(self, endpoint):
        if endpoint in self._known_endpoints:
            return

        self._known_endpoints.add(endpoint)
        handler = web.url(endpoint, _ServiceHandler)
        if self.handlers:
            self.handlers[-1][1].append(handler)
        else:
            self.add_handlers('.*', [handler])

    def get_next_response(self, handler):
        return self.service_layer.get_next_response(handler.request)


class _Service(object):

    def __init__(self):
        super(_Service, self).__init__()
        self.acceptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                      socket.IPPROTO_TCP)
        self.acceptor.setblocking(0)
        self.acceptor.bind(('127.0.0.1', 0))
        self.acceptor.listen(10)
        self.host = '%s:%d' % self.acceptor.getsockname()
        self._responses = collections.defaultdict(list)

    def add_response(self, request, response):
        self._responses[request.method, request.resource].append(response)

    def get_next_response(self, request):
        return self._responses[request.method, request.resource].pop(0)
