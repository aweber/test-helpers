import sys

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

try:
    from unittest import mock
except ImportError:
    import mock

sys.modules[__package__ + '.mock'] = mock
