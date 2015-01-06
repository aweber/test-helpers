Overview
========

The Test Helpers library exists to consolidate some of the repetition that
has arisen in our tests while providing a useful set of generic testing
utilities.

This library offers a set of base test cases, testing mixins, and testing
utilities to make interacting with third party services, testing metrics
generation, and creating mocks or patches easier.


Examples
--------

The library is designed to be simple and modular.  By using mixins to extend
the test cases functionality we can write more expressive tests in fewer lines
of code.

    >>> from test_helpers import mixins, bases
    >>> class WhenFooingBar(mixins.PatchMixin, bases.BaseTest):
    ...
    ...     patch_prefix = 'module.submodule'
    ...
    ...     @classmethod
    ...     def configure(cls):
    ...         cls.foo = cls.create_patch('foo', return_value=True)
    ...
    ...     @classmethod
    ...     def execute(cls):
    ...         function_under_test()
    ...
    ...     def should_have_called_foo(cls):
    ...         self.foo.assert_called_once_with()



Documentation
=============

.. toctree::

   bases
   mixins
   mongo
   postgres
   rabbit
   utils

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

.. include:: ../CHANGELOG
