import re
import sys

import fake_servers
from remembrall import memoize

from test_helpers.compat import mock


class PatchMixin(object):
    """A mixin to allow inline patching and automatic un-patching.

    This mixin adds one new method, ``create_patch`` that will create and
    activate patch objects without having to use the decorator.  This results
    in less pylint errors and not having to think about the order of decorator
    application.

    Example Usage::

        class MyTest(mixins.PatchMixin, bases.BaseTest):

            patch_prefix = 'my_application.module.submodule'

            @classmethod
            def configure(cls):
                cls.foo_mock = cls.create_patch('foo')
                cls.bar_mock = cls.create_patch('bar', reutrn_value=100)

            @classmethod
            def execute(cls):
                function_under_test()

            def should_call_foo(self):
                self.foo_mock.assert_called_once_with()

            def should_return_100_from_bar(self):
                self.assertEqual(100, self.bar_mock.reutrn_value)

    """

    patch_prefix = ''
    """Pattern used to generate fully-qualified patch names."""

    @classmethod
    def setUpClass(cls):
        cls.initalize_patches()
        super(PatchMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.stop_patches()
        super(PatchMixin, cls).tearDownClass()

    @classmethod
    def initalize_patches(cls):
        """Create the list that will contain the active patches."""
        cls._active_patches = []

    @classmethod
    def stop_patches(cls):
        """Stop any active patches when the class is finished."""
        for patcher in cls._active_patches:
            patcher.stop()
        cls._active_patches = []

    @classmethod
    def create_patch(cls, target, **kwargs):
        """Create and apply a patch.

        This method calls :func:`mock.patch` with the keyword parameters
        and returns the running patch.  This approach has the benefit of
        applying a patch without scoping the patched code which, in turn,
        lets you apply patches without having to override :meth:`setUpClass`
        to do it.

        :param str target: the target of the patch.  This is passed as
            an argument to ``cls.patch_prefix.format()`` to create the
            fully-qualified patch target.

        """
        patch_prefix = cls.patch_prefix

        if patch_prefix and not patch_prefix.endswith('.'):
            patch_prefix += '.'

        path = '{0}{1}'.format(patch_prefix, target)
        patcher = mock.patch(path, **kwargs)
        patched = patcher.start()
        cls._active_patches.append(patcher)
        return patched


class MetricsTestMixin(object):
    """Mixin class that provides metric testing functionality.

    By mixing in this class you will gain access to starting and destroying
    a fake UDP server that will act as a stand-in for a StatsD server.  It
    will then become possible to make assertions about the number of metrics
    as well as the type and format of the metrics that the API is producing.

    Example Usage::

        class MyTest(mixins.MetricsTestMixin, bases.BaseTest):

            @classmethod
            def execute(cls):
                metric_generating_function_under_test()

            def should_capture_counter_metric(self):
                self.assert_metric_was_captured(
                    'applications.my_application.counters:?|c',
                )

             def should_capture_timer_metric(self):
                self.assert_metric_was_captured(
                    'applications.my_application.timers:?|ms',
                )

            def should_capture_gauge_metric(self):
                self.assert_metric_was_captured(
                    'applications.my_application.gauges:?|g',
                )

    """

    metrics_port = 8125

    @classmethod
    def setUpClass(cls):
        cls.start_statsd_server()
        super(MetricsTestMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.stop_statsd_server()
        super(MetricsTestMixin, cls).tearDownClass()

    @classmethod
    def start_statsd_server(cls):
        """Create and start a fake statsd server.

        This function will create a fake UDP server and kick it off to
        capture metrics.  The `stop_statsd_server` should be invoked to
        clean up after the test.

        """
        cls.statsd_server = fake_servers.FakeUdpServer(cls.metrics_port)
        cls.statsd_server.start()

    @classmethod
    def stop_statsd_server(cls):
        """Stop the fake UDP server."""
        cls.statsd_server.stop()

    @classmethod
    @memoize
    def get_all_metrics(cls):
        """Consume all of the metrics available on the fake server"""
        return [metric for metric in iter(cls.statsd_server.get_data, None)]

    def assert_metric_was_captured(self, pattern):
        """Assert the metric pattern provided was captured by the server."""
        for metric in self.get_all_metrics():
            if re.match(pattern, metric):
                return True

        self.fail('The provided pattern did not match any captured metrics')
