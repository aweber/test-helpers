from __future__ import print_function

import logging
import os
import re

import requests.models

from test_helpers import bases, mixins, rabbit


class FakeSession(object):
    def __init__(self):
        super(FakeSession, self).__init__()
        self.headers = requests.models.CaseInsensitiveDict()
        self.auth = None
        self._responses = {}
        self.requests = []
        self.log = logging.getLogger('FakeSession')

    def _create_response(self, url, status, headers=None):
        response = requests.Response()
        response.status_code = status
        response.url = url
        if headers:
            response.headers.update(headers)
        return response

    def get(self, *args, **kwargs):
        self.request('GET', *args, **kwargs)

    def put(self, *args, **kwargs):
        self.request('PUT', *args, **kwargs)

    def post(self, *args, **kwargs):
        self.request('POST', *args, **kwargs)

    def delete(self, *args, **kwargs):
        self.request('DELETE', *args, **kwargs)

    def request(self, method, url, **kwargs):
        self.log.debug('RECEIVED %s FOR %s', method, url)
        self.requests.append((method, url, kwargs))
        for patn in self._responses:
            if re.match(patn, url):
                try:
                    return self._responses[patn][method]
                except KeyError:
                    pass
        return self._create_response(url, 200)

    def add_result(self, method, url, status):
        self._responses.setdefault(url, {})
        self._responses[url][method] = self._create_response(url, status)

    def clear_requests(self):
        del self.requests[:]


class _RabbitTestCase(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.rabbit'

    @classmethod
    def configure(cls):
        super(_RabbitTestCase, cls).configure()
        cls.atexit = cls.create_patch('atexit')
        request_module = cls.create_patch('requests')

        cls.session = FakeSession()
        request_module.session.return_value = cls.session
        cls._saved_ampq_var = os.environ.pop('AMQP', None)

        cls.fixture = rabbit.RabbitMqFixture('host', 'user', 'password')

    @classmethod
    def annihilate(cls):
        super(_RabbitTestCase, cls).annihilate()
        os.environ.pop('AMQP', None)
        if cls._saved_ampq_var is not None:
            os.environ['AMQP'] = cls._saved_ampq_var


########
#
# RabbitMqFixture.install_virtual_host
#
########

class _BaseInstallVirtualHostTestCase(_RabbitTestCase):

    @classmethod
    def execute(cls):
        try:
            cls.virtual_host = cls.fixture.install_virtual_host()
        except Exception as exc:
            cls.exception = exc


class WhenInstallingVirtualHostAndVhostPutFails(
        _BaseInstallVirtualHostTestCase):

    @classmethod
    def configure(cls):
        super(WhenInstallingVirtualHostAndVhostPutFails, cls).configure()
        cls.session.add_result(
            'PUT', r'^http://host:15672/api/vhosts/.*', 500)

    def should_not_register_exit_routine(self):
        self.assertFalse(self.atexit.register.called)

    def should_not_make_additional_api_calls(self):
        self.assertEqual(len(self.session.requests), 1)

    def should_raise_exception(self):
        self.assertIsNotNone(self.exception)

    def should_not_export_amqp_variable(self):
        self.assertIsNone(os.environ.get('AMQP', None))


class WhenInstallingVirtualHostAndSetPermissionsFails(
        _BaseInstallVirtualHostTestCase):

    @classmethod
    def configure(cls):
        super(
            WhenInstallingVirtualHostAndSetPermissionsFails, cls).configure()
        cls.session.add_result(
            'PUT', r'^http://host:15672/api/permissions/.*/user$', 500)

    def should_register_exit_routine(self):
        self.atexit.register.assert_called_once_with(
            self.fixture.remove_virtual_host)

    def should_raise_exception(self):
        self.assertIsNotNone(self.exception)

    def should_not_export_amqp_variable(self):
        self.assertIsNone(os.environ.get('AMQP', None))


########
#
# RabbitMqFixture.remove_virtual_host
#
########

class WhenFailingToRemoveVirtualHost(_RabbitTestCase):

    @classmethod
    def configure(cls):
        super(WhenFailingToRemoveVirtualHost, cls).configure()
        cls.session.add_result('DELETE', '.*', 404)
        cls.fixture._virtual_host = '%2F'

    @classmethod
    def execute(cls):
        cls.fixture.remove_virtual_host()

    def should_attempt_delete(self):
        self.assertEqual(len(self.session.requests), 1)


class WhenRemovingVirtualHostTwice(_RabbitTestCase):

    @classmethod
    def configure(cls):
        super(WhenRemovingVirtualHostTwice, cls).configure()
        cls.fixture.install_virtual_host()
        cls.session.clear_requests()
        cls.fixture.remove_virtual_host()

    @classmethod
    def execute(cls):
        cls.fixture.remove_virtual_host()

    def should_only_make_one_request(self):
        self.assertEqual(len(self.session.requests), 1)


########
#
# RabbitMqFixture.create_binding
#
########

class WhenCreatingBindingBeforeVHost(_RabbitTestCase):

    @classmethod
    def execute(cls):
        try:
            cls.fixture.create_binding('exchange', 'queue', 'key')
        except Exception as exc:
            cls.exception = exc

    def should_raise_runtime_error(self):
        self.assertIsInstance(self.exception, RuntimeError)


class _BaseCreateBindingFailureTestCase(_RabbitTestCase):
    @classmethod
    def configure(cls):
        super(_BaseCreateBindingFailureTestCase, cls).configure()
        cls.exception = None
        cls.fixture.install_virtual_host()
        cls.session.clear_requests()

    @classmethod
    def execute(cls):
        try:
            cls.fixture.create_binding('exchange', 'queue', 'router')
        except Exception as exc:
            cls.exception = exc

    def should_raise_exception(self):
        self.assertIsNotNone(self.exception)


class WhenFailingToCreateQueue(_BaseCreateBindingFailureTestCase):

    @classmethod
    def configure(cls):
        super(WhenFailingToCreateQueue, cls).configure()
        cls.session.add_result('PUT', '.*/api/queues/.*', 400)

    def should_make_one_request(self):
        self.assertEqual(len(self.session.requests), 1)


class WhenFailingToCreateExchange(_BaseCreateBindingFailureTestCase):

    @classmethod
    def configure(cls):
        super(WhenFailingToCreateExchange, cls).configure()
        cls.session.add_result('PUT', '.*/exchanges/.*', 400)

    def should_make_two_requests(self):
        self.assertEqual(len(self.session.requests), 2)


class WhenFailingToCreateBinding(_BaseCreateBindingFailureTestCase):

    @classmethod
    def configure(cls):
        super(WhenFailingToCreateBinding, cls).configure()
        cls.session.add_result('POST', '.*/bindings/.*', 400)

    def should_make_three_requests(self):
        self.assertEqual(len(self.session.requests), 3)


########
#
# RabbitMqFixture.purge_queue
#
########

class WhenFailingToPurgeQueue(_RabbitTestCase):
    @classmethod
    def configure(cls):
        super(WhenFailingToPurgeQueue, cls).configure()
        cls.fixture.install_virtual_host()
        cls.session.clear_requests()
        cls.exception = None

        cls.session.add_result('DELETE', '.*', 400)

    @classmethod
    def execute(cls):
        try:
            cls.fixture.purge_queue('q')
        except Exception as exc:
            cls.exception = exc

    def should_make_a_request(self):
        self.assertEqual(len(self.session.requests), 1)

    def should_raise_exception(self):
        self.assertIsNotNone(self.exception)
