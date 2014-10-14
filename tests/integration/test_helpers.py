from __future__ import absolute_import

from test_helpers.bases import BaseTest
from test_helpers import utils

ppatch = utils.create_ppatch('tests.integration.test_helpers')


#########
#
# mixins.PatchMixin
#
#########


class WhenCreatingAPartialPatch(BaseTest):

    @classmethod
    @ppatch('function_under_test', return_value='foobar')
    def configure(cls, mocked):
        cls.mocked = mocked

    @classmethod
    def execute(cls):
        cls.result = cls.mocked()

    def should_have_called_the_mocked_function(self):
        self.assertEqual(self.result, 'foobar')
