|BuildStatus| |CoverageStatus| |Downloads| |License| |Docs|

.. |BuildStatus| image:: https://travis-ci.org/aweber/test-helpers.svg
   :target: https://travis-ci.org/aweber/test-helpers
.. |CoverageStatus| image:: https://coveralls.io/repos/aweber/test-helpers/badge.png
   :target: https://coveralls.io/r/aweber/test-helpers
.. |Downloads| image:: https://pypip.in/download/test-helpers/badge.svg
   :target: https://pypi.python.org/pypi/test-helpers/
.. |License| image:: https://pypip.in/license/test-helpers/badge.svg
   :target: https://pypi.python.org/pypi/test-helpers/
.. |Docs| image:: https://readthedocs.org/projects/test-helpers/badge/?version=latest
   :target: http://test-helpers.readthedocs.org/en/latest/

Test Helpers
============

The Test Helpers library aims to make `Arrange-Act-Assert`_, class-based tests easier
to write.  The helpers in this module make patching easier, ease Python 3 compatibility,
and gently guide users towards the AAA style of testing.  Additional helpers are included
for situations likely to be encountered in the web-app world.


Examples
--------

The library is designed to be simple and modular.  By using mixins to extend
the test cases functionality we can write more expressive tests in fewer lines
of code.

Creating Patches::

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


Tornado-related Extensions
--------------------------

The Test Helpers library includes a number of helpers specific to testing
Tornado-based applications.  Before you can use any of the Tornado helpers,
you must either:

1. install Tornado as a dependency *OR*
2. include a dependency on ``test_helpers[tornado]`` in your pip requirements

Dependent Data Service Helpers
------------------------------

The Test Helpers library includes classes that facilitate initializing and
cleaning up dependent data service resources. Provided with connection
configuration to existing service instances, each class can generate name-spaced
workspaces and tear down any created workspaces at the end of each test run.

Currently included:

- MongoDB
- PostgreSQL
- RabbitMQ

Supported Python Versions
--------------------------

The Test Helpers library is built and tested against python 2.6, 2.7, and 3.3.
You may need to grab other versions of the interpreter with your preferred package
manager (MacPorts, Apt, Yum, etc)

``sudo port install python27 python33``


Running Tests
-------------

To run the all of the tests across the supported versions of Python via
``tox`` run the following commands in your terminal::

    make test


Developing The Test Helpers library
-----------------------------------

Clone the repo and start hacking::

    $ make requirements # If you just cloned the repo or requirements.pip changes
    $ make test # Run the tests afterwards to ensure everything is running as expected

Authors
-------
Dan Tracy, `John Brodie`_ at `AWeber Communications`_

.. _Arrange-Act-Assert: http://c2.com/cgi/wiki?ArrangeActAssert
.. _John Brodie: http://brodie.me
.. _AWeber Communications: http://www.aweber.com
