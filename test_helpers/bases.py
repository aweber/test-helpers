"""
===============
Base Test Cases
===============

The base test cases module contains useful classes that inherit from the
unit test standard library and optionally inherit from an arbitrary number of
mixins.  The purpose of these classes is to provide an integration point for
the mixins and to help promote the usage of the Arrange-Act-Assert testing
methodology used here at AWeber.

"""
from test_helpers.compat import unittest


class BaseTest(unittest.TestCase):
    """Base class for the AWeber AAA testing style.

    This implements the Arrange-Act-Assert style of unit testing though
    the names were chosen to match existing convention.  New unit tests
    should use this as a base class and replace the :meth:`configure` and
    :meth:`execute` methods as necessary.

    """

    maxDiff = 100000

    @classmethod
    def setUpClass(cls):
        """Arrange the test and do the action.

        If you are extending this method, then you are required to call
        this implementation as the last thing in your version of this
        method.

        """
        super(BaseTest, cls).setUpClass()
        cls.configure()
        cls.execute()

    @classmethod
    def configure(cls):
        """Extend to configure your test environment."""
        pass

    @classmethod
    def execute(cls):
        """Override to execute your test action."""
        raise NotImplementedError('The execute action was not defined!')
