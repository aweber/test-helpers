import sys

if sys.version_info >= (2, 7):  # pragma: no cover
    import unittest
else:
    import unittest2 as unittest

try:
    from unittest import mock
except ImportError:
    import mock
