"""
Testing
-------
Cross-version imports of testing tools.

This module allows tests to run under all
recent Python versions without requiring changes
to each import in our tests.

Both mock and unittest should be imported from
this module to reap these benefits.  For example:

    from tests.mock import Mock, patch
    from tests import unittest

"""

import sys

if sys.version_info >= (2, 7):
    import unittest  # pragma: no cover
else:
    import unittest2 as unittest  # pragma: no cover

try:
    from unittest import mock  # pragma: no cover
except ImportError:
    import mock  # pragma: no cover

sys.modules[__package__ + '.mock'] = mock
sys.modules[__package__ + '.unittest'] = unittest
