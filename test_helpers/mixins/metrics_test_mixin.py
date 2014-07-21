import re

from remembrall import memoize
import fake_servers


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
