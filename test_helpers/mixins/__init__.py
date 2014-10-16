"""Collection of functionality mix-ins.

This module contains standalone classes that can be safely mixed
into the :class:`~test_helpers.bases.BaseTest` class.  Each mixin
extends the functionality of the test case by adding behaviors,
methods, and attributes - for example, patching well-understood
functionality or automatically creating/destroying an in memory
UDP server.

When creating a mixin it is important to take not that you
should strive to keep the Method Resolution Order (MRO) as clean
as possible.  Each mixin class should ideally only inherit from
``object``.

"""

from .patch_mixin import PatchMixin

__all__ = ('PatchMixin')
