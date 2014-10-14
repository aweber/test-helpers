"""
Testing Utilities
=================

The testing utilities module contains standalone functionality for that might
be useful for a select number of test cases.  These functions can be
selectively applied to a small subset of tests so they might not warrant the
full capacity of mixin behavior.

The utilities within this module are typically simple functions or decorators
that ease a specific testing task, such as creating patches.

"""

import functools

from test_helpers.compat import mock


def create_ppatch(path):
    """Create a partial ppatch object that will only require the object name"""
    return functools.partial(ppatch, path)


def ppatch(path, object_name, **kwargs):
    """Creates a fully qualified patch object.

    This function will act as a wrapper that will allow us to create a partial
    function representation.  That will remove the need to keep passing the
    same path to the patch object.

    """
    return mock.patch(path.format(object_name), **kwargs)
