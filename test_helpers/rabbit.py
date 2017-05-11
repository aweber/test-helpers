import atexit
import json
import os
import uuid

try:
    from urllib import parse
except ImportError:  # pragma no cover
    import urllib as parse

import requests


class RabbitMqFixture(object):
    """
    Manages a Rabbit MQ virtual host.

    Create an instance of this class when you need to programmatically
    manage a Rabbit MQ cluster.  Pika gives you the ability to create
    exchanges and queues and bind them together using the AMQP protocol
    but there is no way to create a new virtual host.  Despite that,
    running tests on randomly unique virtual hosts is quite convenient.

    This class uses Rabbit's HTTP API to manipulate the cluster.  It
    exposes the management functions that have proven useful for writing
    tests against a shared RabbitMQ cluster.

    **Usage Example**

    .. code-block:: python

       from test_helpers import rabbit

       _fixture = rabbit.RabbitMqFixture('localhost', 'guest', 'guest')

       def setup_module():
           _fixture.install_virtual_host()
           _fixture.create_binding('accounts', 'my_queue', 'status.added')

           # from this point on, os.environ['AMQP'] points to a
           # newly created, isolated virtual host that will be
           # removed when the test is complete

    """

    def __init__(self, host, user, password, port=5672, mgmt_port=15672):
        super(RabbitMqFixture, self).__init__()
        self._host = parse.quote(host, safe='')
        self._port = int(port)
        self._mgmt_port = int(mgmt_port)
        self._session = requests.session()
        self._session.headers['Content-Type'] = 'application/json'
        self._session.auth = (user, password)
        self._virtual_host = None

    @property
    def virtual_host(self):
        """The URL-quoted virtual host ready to use as-is."""
        return self._virtual_host

    @property
    def host(self):
        """The URL-quoted rabbit server."""
        return self._host

    @property
    def user(self):
        """The URL-quoted rabbit user name."""
        return parse.quote(self._session.auth[0], safe='')

    @property
    def password(self):
        """The URL-quoted rabbit password."""
        return parse.quote(self._session.auth[1], safe='')

    @property
    def port(self):
        """The RabbitMQ service port."""
        return self._port

    @property
    def mgmt_port(self):
        """The RabbitMQ cluster management port."""
        return self._mgmt_port

    def install_virtual_host(self):
        """
        Create a new virtual host.

        :returns: the name of the virtual host

        The virtual host will be created and the current user will
        be granted full permission to it.

        This method also sets the :envvar:`AMQP` environment
        variable to the appropriate URL for connecting to the
        virtual host.

        """
        self._virtual_host = parse.quote('/' + uuid.uuid4().hex, safe='')
        self._rabbit_api_request(
            'PUT', 'vhosts', self.virtual_host,
        ).raise_for_status()
        atexit.register(self.remove_virtual_host)

        self._rabbit_api_request(
            'PUT', 'permissions', self.virtual_host, self.user,
            data={'configure': '.*', 'write': '.*', 'read': '.*'},
        ).raise_for_status()

        os.environ['AMQP'] = 'amqp://{0}:{1}@{2}:{3}/{4}'.format(
            self.user, self.password, self.host, self.port,
            self.virtual_host)

        return self._virtual_host

    def remove_virtual_host(self):
        """Remove the generated virtual host."""
        if self.virtual_host:
            self._rabbit_api_request('DELETE', 'vhosts', self.virtual_host)
            self._virtual_host = None

    def create_binding(self, exchange_name, queue_name, routing_key):
        """
        Create a message binding.

        :param str exchange_name: name of the exchange to create/update
        :param str queue_name: name of the queue to create/update
        :param str routing_key: routing key that binds the exchange
            and the queue

        This method creates the specified queue and exchange if they
        do not already exist and then binds `routing_key` such that
        messages with it are routed through the exchange and queue.

        """
        if not self.virtual_host:
            raise RuntimeError(
                'attempted to create a binding without a virtual host')

        exchange_name = parse.quote(exchange_name, safe='')
        queue_name = parse.quote(queue_name, safe='')

        self._rabbit_api_request(
            'PUT', 'queues', self.virtual_host, queue_name,
            data={'auto_delete': False, 'durable': False},
        ).raise_for_status()
        self._rabbit_api_request(
            'PUT', 'exchanges', self.virtual_host, exchange_name,
            data={'type': 'topic', 'durable': False},
        ).raise_for_status()
        self._rabbit_api_request(
            'POST', 'bindings', self.virtual_host,
            'e', exchange_name, 'q', queue_name,
            data={'routing_key': routing_key},
        ).raise_for_status()

    def purge_queue(self, queue_name):
        """Purge a Rabbit MQ queue."""
        self._rabbit_api_request(
            'DELETE', 'queues', self.virtual_host,
            parse.quote(queue_name, safe=''), 'contents',
        ).raise_for_status()

    def _rabbit_api_request(self, method, *path, **kwargs):
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data']).encode('utf-8')
        return self._session.request(
            method,
            'http://{0}:{1}/api/{2}'.format(
                self.host, self.mgmt_port, '/'.join(path)),
            **kwargs
        )
