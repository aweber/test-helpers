from __future__ import absolute_import

import os
import uuid

from test_helpers import bases, mixins


#########
#
# mixins.PatchMixin
#
#########

class WhenTestingPatchingMixin(mixins.PatchMixin, bases.BaseTest):

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
# mixins.EnvironmentMixin
#
#########

class WhenUsingEnvironmentMixin(mixins.EnvironmentMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenUsingEnvironmentMixin, cls).configure()
        cls.var_name = uuid.uuid4().hex
        cls.saved_path = os.environ['PATH']
        assert cls.var_name not in os.environ

    @classmethod
    def execute(cls):
        cls.set_environment_variable(cls.var_name, 'BAR')
        cls.unset_environment_variable('PATH')

    def should_set_environment_variable(self):
        self.assertEqual(os.environ[self.var_name], 'BAR')

    def should_clear_environment_variable(self):
        self.assertNotIn('PATH', os.environ)

    @classmethod
    def tearDownClass(cls):
        super(WhenUsingEnvironmentMixin, cls).tearDownClass()
        if cls.var_name in os.environ:
            raise AssertionError('variable not removed from environment')
        if 'PATH' not in os.environ or os.environ['PATH'] != cls.saved_path:
            raise AssertionError('variable not restored to environment')
