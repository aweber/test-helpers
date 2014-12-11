import os


class EnvironmentMixin(object):
    """
    Mix this class in if you manipulate environment variables.

    A common problem in testing code that uses environment variables
    is forgetting that they are really globals that persist between
    tests.  This mixin exposes methods that make it easy and safe to
    set and unset environment variables while ensuring that the
    environment will be restored when the test has completed.

    You need to mix this in over a class that calls the ``configure``
    ``annihilate`` class methods around the code under test such as
    :class:`test_helpers.bases.BaseTest`.

    """

    @classmethod
    def configure(cls):
        super(EnvironmentMixin, cls).configure()
        cls._saved_environment = {}

    @classmethod
    def annihilate(cls):
        super(EnvironmentMixin, cls).annihilate()
        for key, value in cls._saved_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls._saved_environment.clear()

    @classmethod
    def set_environment_variable(cls, name, value):
        """Set the value of an environment variable."""
        cls._stash_current(name)
        os.environ[name] = value

    @classmethod
    def unset_environment_variable(cls, name):
        """Clear an environment variable."""
        cls._stash_current(name)
        os.environ.pop(name, None)

    @classmethod
    def _stash_current(cls, name):
        if name not in cls._saved_environment:
            cls._saved_environment[name] = os.environ.get(name, None)
