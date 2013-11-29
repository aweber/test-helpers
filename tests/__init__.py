import sys

try:
    import unittest
except ImportError:
    import unittest2 as unittest

try:
    from unittest import mock
except ImportError:
    import mock

sys.modules[__package__ + '.mock'] = mock
