from .. compat import mock


class PatchMixin(object):
    """A mixin to allow inline patching and automatic un-patching.

    This mixin adds one new method, ``create_patch`` that will create and
    activate patch objects without having to use the decorator.

    In order to make use of the patching functionality you need to set
    the ``patch_prefix`` class attribute.  This attribute should be the python
    module path whose objects you want to patch.  For example, if you wanted
    to patch the ``baz`` object in the ``foo.bar`` module your patch prefix
    might look like ``foo.bar``.  When creating a patch you can now just refer
    to the object name like ``cls.create_patch('baz')``.

    This usage of this mixin as opposed to the patch decorator results
    in less pylint errors and not having to think about the order of decorator
    application.

    Example Usage::

        class MyTest(mixins.PatchMixin, bases.BaseTest):

            patch_prefix = 'my_application.module.submodule'

            @classmethod
            def configure(cls):
                cls.foo_mock = cls.create_patch('foo')
                cls.bar_mock = cls.create_patch('bar', return_value=100)

            @classmethod
            def execute(cls):
                function_under_test()

            def should_call_foo(self):
                self.foo_mock.assert_called_once_with()

            def should_return_100_from_bar(self):
                self.assertEqual(100, self.bar_mock.return_value)

    """

    patch_prefix = ''
    """Pattern used to generate fully-qualified patch names."""

    @classmethod
    def setUpClass(cls):
        cls._active_patches = []
        super(PatchMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.stop_patches()
        super(PatchMixin, cls).tearDownClass()

    @classmethod
    def stop_patches(cls):
        """Stop any active patches when the class is finished."""
        for patcher in cls._active_patches:
            patcher.stop()
        cls._active_patches = []

    @classmethod
    def create_patch(cls, target, **kwargs):
        """Create and apply a patch.

        This method calls :func:`mock.patch` with the keyword parameters
        and returns the running patch.  This approach has the benefit of
        applying a patch without scoping the patched code which, in turn,
        lets you apply patches without having to override :meth:`setUpClass`
        to do it.

        :param str target: the target of the patch.  This is passed as
            an argument to ``cls.patch_prefix.format()`` to create the
            fully-qualified patch target.

        """
        patch_prefix = cls.patch_prefix

        if patch_prefix and not patch_prefix.endswith('.'):
            patch_prefix += '.'

        path = '{0}{1}'.format(patch_prefix, target)
        patcher = mock.patch(path, **kwargs)
        patched = patcher.start()
        cls._active_patches.append(patcher)
        return patched
