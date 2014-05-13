from __future__ import absolute_import

from test_helpers import url
from tests import unittest


#########
#
# url.assert_url_equal
#
#########


class WhenComparingURLs(unittest.TestCase):

    def should_not_explode_when_the_args_differ_in_order(self):
        url.assert_url_equal(
            'http://www.google.com?q=foo&arg=baz',
            'http://www.google.com?arg=baz&q=foo',
        )
