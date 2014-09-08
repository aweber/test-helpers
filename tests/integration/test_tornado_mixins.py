from __future__ import absolute_import

from tornado import web

from test_helpers import bases, mixins
from test_helpers.mixins import tornado


class RecordingRequestHandler(web.RequestHandler):

    def on_request(self, *args, **kwargs):
        self.application.record_request(self.request)
        self.set_status(200)

    delete = on_request
    get = on_request
    head = on_request
    options = on_request
    post = on_request
    put = on_request


class Recorder(web.Application):

    def __init__(self):
        super(Recorder, self).__init__(handlers=[
            ('/', RecordingRequestHandler),
        ])
        self.requests = []

    def record_request(self, request):
        self.requests.append(request)


class _TornadoMixinTestCase(mixins.PatchMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(_TornadoMixinTestCase, cls).configure()
        cls.application = Recorder()
        cls.test_instance = tornado.TornadoMixin
        cls.test_instance.start_tornado(cls.application)

    @classmethod
    def annihilate(cls):
        super(_TornadoMixinTestCase, cls).annihilate()
        cls.test_instance.stop_tornado()

    @property
    def request(self):
        return self.application.requests[0]

    def should_issue_single_request(self):
        self.assertEqual(len(self.application.requests), 1)


class WhenTornadoMixinGets(_TornadoMixinTestCase):

    @classmethod
    def execute(cls):
        cls.test_instance.get('/')

    def should_get_from_request_handler(self):
        self.assertEqual(self.request.method, 'GET')

    def should_get_requested_path(self):
        self.assertEqual(self.request.path, '/')


class WhenTornadoMixinPosts(_TornadoMixinTestCase):

    @classmethod
    def execute(cls):
        cls.test_instance.post('/', 'body')

    def should_post_to_request_handler(self):
        self.assertEqual(self.request.method, 'POST')

    def should_post_to_requested_path(self):
        self.assertEqual(self.request.path, '/')

    def should_post_body(self):
        self.assertEqual(self.request.body, b'body')


class WhenTornadoMixinDeletes(_TornadoMixinTestCase):

    @classmethod
    def execute(cls):
        cls.test_instance.delete('/')

    def should_send_delete_to_request_handler(self):
        self.assertEqual(self.request.method, 'DELETE')

    def should_delete_requested_resource(self):
        self.assertEqual(self.request.path, '/')


class WhenTornadoMixinPuts(_TornadoMixinTestCase):

    @classmethod
    def execute(cls):
        cls.test_instance.put('/', 'body')

    def should_put_to_request_handler(self):
        self.assertEqual(self.request.method, 'PUT')

    def should_put_to_requested_path(self):
        self.assertEqual(self.request.path, '/')

    def should_put_body(self):
        self.assertEqual(self.request.body, b'body')


class WhenTornadoMixinRequestsOptions(_TornadoMixinTestCase):

    @classmethod
    def execute(cls):
        cls.test_instance.request('OPTIONS', '/')

    def should_request_options__from_request_handler(self):
        self.assertEqual(self.request.method, 'OPTIONS')

    def should_request_appropriate_resource(self):
        self.assertEqual(self.request.path, '/')
