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
