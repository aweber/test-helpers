"""
==============
Testing Mixins
==============

The testing mixins module contains standalone classes that can be safely
mixed into the :class:`~test_helpers.bases.BaseTest` class.  These mixins
extend the functionality of the test case by adding nice features or methods
such as patching functionality or automatic creation/destruction of an in
memory UDP server.

When creating a mixin it is important to take not that you should strive to
keep the Method Resolution Order (MRO) as clean as possible.  The mixin
classes should ideally only inherit from ``object``.

"""

from . metrics_test_mixin import MetricsTestMixin
from . patch_mixin import PatchMixin
from . tornado import TornadoMixin


__all__ = (
    'MetricsTestMixin',
    'PatchMixin',
    'TornadoMixin',
)
