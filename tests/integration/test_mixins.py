from __future__ import absolute_import

import socket

from test_helpers.bases import BaseTest
from test_helpers import mixins


#########
#
# mixins.PatchMixin
#
#########


class WhenTestingPatchingMixin(mixins.PatchMixin, BaseTest):

    patch_prefix = 'tests.integration.test_mixins'

    @classmethod
    def configure(cls):
        cls.mocked = cls.create_patch('function_under_test', create=True)
        cls.mocked.return_value = 'foobar'

    @classmethod
    def execute(cls):
        cls.result = cls.mocked()

    def should_have_called_the_mocked_function(self):
        self.assertEqual(self.result, 'foobar')


#########
#
# mixins.PatchMixin
#
#########

class WhenTestingMetricsCollection(mixins.MetricsTestMixin, BaseTest):

    metrics_port = 8125

    @classmethod
    def execute(cls):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b'Hello World', ('localhost', cls.metrics_port))

    def should_capture_the_metric(self):
        self.assert_metric_was_captured('Hello World')
