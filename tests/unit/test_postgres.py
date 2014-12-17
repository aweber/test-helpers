import psycopg2

from test_helpers import bases, compat, postgres


class WhenCreatingDatabaseMoreThanOnce(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingDatabaseMoreThanOnce, cls).configure()
        cls.db_object = postgres.TemporaryDatabase()
        cls.db_object._run_ddl = compat.mock.Mock()

    @classmethod
    def execute(cls):
        cls.db_object.create()
        cls.db_object.create()

    def should_only_run_ddl_once(self):
        self.assertEqual(self.db_object._run_ddl.call_count, 1)
