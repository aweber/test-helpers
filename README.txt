Test Helpers
============

The Test Helpers library help consolidates some of the common testing utilities
that we have come up with across several project.  The helpers within this
module aim to ease testing metrics collection, make patching easier, and
enforce the common Arrange-Act-Assert type of tests that we write here at
AWeber.


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


Testing metrics generation:

    >>> from test_helpers import mixins, bases
    >>> class WhenGettingMetrics(mixins.MetricsTestMixin, bases.BaseTest):
    ...
    ...     @classmethod
    ...     def execute(cls):
    ...         function_under_test()
    ...
    ...     def should_have_generated_metric_baz(cls):
    ...         self.assert_metric_captured('my.metric.path:?|c')


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
You may need to grab the python 2.7 and 3.3 interpreters via Macports.

`sudo port install python27 python33`


Running Tests
-------------

To run the all of the tests across the supported versions of Python via
``tox`` run the following commands in your terminal.

    make test


Developing The Test Helpers library
-----------------------------------

Clone the mongo backup repo and start hacking.

    $ git clone git@github.colo.lair:aweber/test_helpers.git
    $ cd test_helpers
    $ make requirements # If you just cloned the repo or requirements.pip changes
    $ make test # Run the tests afterwards to ensure everything is running as expected


Programming Standards
---------------------
[We follow the Python Coding Standards](http://legacy.python.org/dev/peps/pep-0008/)
