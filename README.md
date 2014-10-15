[![Build Status](https://travis-ci.org/aweber/test-helpers.svg)](https://travis-ci.org/aweber/test-helpers) [![Coverage Status](https://coveralls.io/repos/aweber/test-helpers/badge.png)](https://coveralls.io/r/aweber/test-helpers) [![Downloads](https://pypip.in/download/test-helpers/badge.svg)](https://pypi.python.org/pypi/test-helpers/) [![License](https://pypip.in/license/test-helpers/badge.svg)](https://pypi.python.org/pypi/test-helpers/) [![Docs](https://readthedocs.org/projects/test-helpers/badge/?version=latest)](http://test-helpers.readthedocs.org/en/latest/)

Test Helpers
============

The Test Helpers library aims to make [Arrange-Act-Assert][1], class-based tests easier
to write.  The helpers in this module make patching easier, ease Python 3 compatibility,
and gently guide users towards the AAA style of testing.  Additional helpers are included
for situations likely to be encountered in the web-app world.


Examples
--------

The library is designed to be simple and modular.  By using mixins to extend
the test cases functionality we can write more expressive tests in fewer lines
of code.

Creating Patches:

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

1. install Tornado as a dependency _OR_
2. include a dependency on 'test_helpers[tornado]' in your pip requirements


Supported Python Versions
--------------------------

The Test Helpers library is built and tested against python 2.6, 2.7, and 3.3.
You may need to grab other versions of the interpreter with your preferred package
manager (MacPorts, Apt, Yum, etc)

`sudo port install python27 python33`


Running Tests
-------------

To run the all of the tests across the supported versions of Python via
``tox`` run the following commands in your terminal.

    make test


Developing The Test Helpers library
-----------------------------------

Clone the repo and start hacking

    $ make requirements # If you just cloned the repo or requirements.pip changes
    $ make test # Run the tests afterwards to ensure everything is running as expected

Authors
-------
Dan Tracy, [John Brodie][2] at [AWeber Communications][3]

[1]: http://c2.com/cgi/wiki?ArrangeActAssert
[2]: http://brodie.me
[3]: http://www.aweber.com
