from __future__ import absolute_import

import logging
import json
import os
import socket

import requests

from test_helpers import bases, mixins, rabbit


RABBIT_HOST = os.environ.get('RABBITMQ', 'localhost')
logging.getLogger('requests').setLevel(logging.DEBUG)

# The following makes our tests still work when RabbitMQ is unavailable.
# This is the painful version of @unittest.skipIf() that actually works
# across the different Python versions reliably.  It takes advantage of
# the fact that nose, py.test, and most test runners look at the __test__
# attribute of an object and skip it if the attribute is falsy.
_rabbit_sock = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
try:
    _rabbit_sock.connect((RABBIT_HOST, 5672))
except:
    __test__ = False
finally:
    _rabbit_sock.close()


class _BaseRabbitTestCase(mixins.EnvironmentMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(_BaseRabbitTestCase, cls).configure()
        cls.fixture = rabbit.RabbitMqFixture(
            host=RABBIT_HOST, user='guest', password='guest')
        cls.unset_environment_variable('AMQP')

    @staticmethod
    def make_api_request(*paths, **kwargs):
        method = kwargs.pop('method', 'GET')
        kwargs.setdefault('auth', ('guest', 'guest'))
        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Content-Type', 'application/json')

        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data']).encode('utf-8')

        url = 'http://{0}:15672/api/{1}'.format(RABBIT_HOST, '/'.join(paths))
        return requests.request(method, url, **kwargs)


class WhenInstallingUnnamedVirtualHost(_BaseRabbitTestCase):

    @classmethod
    def execute(cls):
        cls.virtual_host = cls.fixture.install_virtual_host()

    def should_return_virtual_host_name(self):
        self.assertIsNotNone(self.virtual_host)

    def should_create_virtual_host(self):
        response = self.make_api_request('vhosts', self.virtual_host)
        self.assertEqual(response.status_code, 200)

    def should_assign_permissions(self):
        response = self.make_api_request(
            'permissions', self.virtual_host, 'guest')
        response.raise_for_status()
        perms = response.json()
        self.assertEqual(perms['configure'], '.*')
        self.assertEqual(perms['read'], '.*')
        self.assertEqual(perms['write'], '.*')

    def should_export_amqp_environment_variable(self):
        self.assertEqual(
            os.environ['AMQP'],
            'amqp://guest:guest@{0}:5672/{1}'.format(
                RABBIT_HOST, self.virtual_host),
        )


class WhenRemovingUnnamedVirtualHost(_BaseRabbitTestCase):

    @classmethod
    def configure(cls):
        super(WhenRemovingUnnamedVirtualHost, cls).configure()
        cls.virtual_host = cls.fixture.install_virtual_host()

    @classmethod
    def execute(cls):
        cls.fixture.remove_virtual_host()

    def should_delete_virtual_host(self):
        response = self.make_api_request('vhosts', self.virtual_host)
        self.assertEqual(response.status_code, 404)


class WhenCreatingBinding(_BaseRabbitTestCase):

    @classmethod
    def configure(cls):
        super(WhenCreatingBinding, cls).configure()
        cls.fixture.install_virtual_host()
        cls._rabbit_holes = {}

    @classmethod
    def execute(cls):
        cls.fixture.create_binding('my_exchange', 'a_queue', 'router')

    def find_amqp_element(self, name, path):
        if name not in self._rabbit_holes:
            rsp = self.make_api_request(path, self.fixture.virtual_host)
            rsp.raise_for_status()
            for info in rsp.json():
                if info['name'] == name:
                    self._rabbit_holes[name] = info.copy()
                    break
            if name not in self._rabbit_holes:
                self.fail('failed to find %s in %r' % (name, rsp.json()))
        return self._rabbit_holes.get(name, None)

    def should_create_queue(self):
        self.assertIsNotNone(self.find_amqp_element('a_queue', 'queues'))

    def should_create_exchange(self):
        self.assertIsNotNone(
            self.find_amqp_element('my_exchange', 'exchanges'))

    def should_create_binding(self):
        rsp = self.make_api_request('bindings', self.fixture.virtual_host)
        rsp.raise_for_status()
        for binding_info in rsp.json():
            if (binding_info['routing_key'] == 'router' and
                    binding_info['destination'] == 'a_queue' and
                    binding_info['source'] == 'my_exchange' and
                    binding_info['destination_type'] == 'queue'):
                return
        self.fail('failed to find binding in %r' % rsp.json())


class WhenPurgingQueue(_BaseRabbitTestCase):

    @classmethod
    def configure(cls):
        super(WhenPurgingQueue, cls).configure()
        cls.fixture.install_virtual_host()
        cls.fixture.create_binding('e', 'q', 'r')
        # enqueue a message using HTTP API
        cls.make_api_request(
            'exchanges', cls.fixture.virtual_host, 'e', 'publish',
            method='POST',
            data={'properties': {}, 'routing_key': 'r',
                  'payload': '', 'payload_encoding': 'string'},
        )

    @classmethod
    def execute(cls):
        cls.fixture.purge_queue('q')

    def should_remove_queued_messages(self):
        # retrieve a message w/requeue enabled
        response = self.make_api_request(
            'queues', self.fixture.virtual_host, 'q', 'get',
            method='POST',
            data={'count': 1, 'requeue': True, 'encoding': 'auto'},
        )
        response.raise_for_status()
        self.assertEqual(len(response.json()), 0)
