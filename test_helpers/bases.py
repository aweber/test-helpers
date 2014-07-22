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
        try:
            cls.configure()
            cls.execute()
        except:
            cls.annihilate()
            raise

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.annihilate()

    @classmethod
    def configure(cls):
        """Extend to configure your test environment."""
        pass

    @classmethod
    def annihilate(cls):
        """Clean up after a test.

        Unlike :meth:`tearDownClass`, this method is guaranteed to
        be called in all cases.  It will be called even if
        :meth:`configure` fails so do not do anything that depends
        on it having been successful without checking if it was.

        """
        pass

    @classmethod
    def execute(cls):
        """Override to execute your test action."""
        raise NotImplementedError('The execute action was not defined!')
