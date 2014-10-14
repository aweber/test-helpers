from __future__ import absolute_import

from tornado import httpclient

from test_helpers.compat import mock
from test_helpers import bases, mixins
from test_helpers.mixins import tornado


class _JsonMixinTestCase(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.mixins.tornado'

    @classmethod
    def configure(cls):
        cls.real_response = httpclient.HTTPResponse(
            request=mock.Mock(), code=200, buffer=mock.Mock())
        super_lookup = cls.create_patch('super', create=True)
        cls.super_request = super_lookup.return_value.request
        cls.super_request.return_value = cls.real_response

        cls.mixin = tornado.JsonMixin()
        cls.request_kwargs = {}

    @classmethod
    def execute(cls):
        cls.response = cls.mixin.request(
            mock.sentinel.method, **cls.request_kwargs)

    def should_return_response_object(self):
        self.assertIs(self.response, self.real_response)


class WhenJsonMixinRequestsWithoutBody(_JsonMixinTestCase):

    def should_call_super_request_with_accept_header(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            headers={'Accept': 'application/json'},
        )

    def should_set_json_to_none_on_response_object(self):
        self.assertIsNone(self.response.json)


class WhenJsonMixinRequestsWithJsonBody(_JsonMixinTestCase):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinRequestsWithJsonBody, cls).configure()
        cls.request_kwargs['body'] = {'foo': 'bar'}

    def should_use_jsonified_body_in_request(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            body='{"foo": "bar"}'.encode('utf-8'),
            headers=mock.ANY,
        )

    def should_use_appropriate_headers(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            body=mock.ANY,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json',
            },
        )


class WhenJsonMixinRequestsWithJsonBodyAndCustomMimeType(
        WhenJsonMixinRequestsWithJsonBody):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinRequestsWithJsonBodyAndCustomMimeType, cls).configure()
        cls.request_kwargs['headers'] = {
            'content-type': 'application/vnd.aweber.com-login+json',
        }

    def should_use_appropriate_headers(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            body=mock.ANY,
            headers={
                'Content-Type': 'application/vnd.aweber.com-login+json',
                'Accept': 'application/json',
            },
        )


class WhenJsonMixinRequestsWithNonJsonBody(_JsonMixinTestCase):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinRequestsWithNonJsonBody, cls).configure()
        cls.request_kwargs['body'] = mock.sentinel.body
        cls.request_kwargs['headers'] = {
            'content-type': 'application/x-www-form-urlencoded',
        }

    def should_pass_unaltered_body(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            body=mock.sentinel.body,
            headers=mock.ANY,
        )

    def should_use_appropriate_headers(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            body=mock.ANY,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }
        )


class WhenJsonMixinRequestsWithCustomAcceptHeader(_JsonMixinTestCase):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinRequestsWithCustomAcceptHeader, cls).configure()
        cls.request_kwargs['headers'] = {'accept': 'text/html'}

    def should_pass_custom_accept_header(self):
        self.super_request.assert_called_once_with(
            mock.sentinel.method,
            headers={'Accept': 'text/html'},
        )


class WhenJsonMixinGetsJsonResponse(_JsonMixinTestCase):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinGetsJsonResponse, cls).configure()
        cls.json_loads = cls.create_patch('json').loads
        cls.real_response.headers['content-type'] = (
            'application/json; charset=utf8')
        cls.real_response._body = b'{"body":"value"}'

    def should_json_loads_response_body(self):
        self.json_loads.assert_called_once_with('{"body":"value"}')

    def should_save_json_on_response_object(self):
        self.assertIs(
            self.response.json, self.json_loads.return_value)


class WhenJsonMixinGetsNonJsonResponse(_JsonMixinTestCase):

    @classmethod
    def configure(cls):
        super(WhenJsonMixinGetsNonJsonResponse, cls).configure()
        cls.real_response.headers['content-type'] = 'text/plain'

    def should_set_json_to_none_on_response_object(self):
        self.assertIsNone(self.response.json)
