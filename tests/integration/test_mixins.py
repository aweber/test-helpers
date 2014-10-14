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
