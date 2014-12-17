import psycopg2

from test_helpers import bases, compat, mixins, postgres


class WhenRemovingDatabases(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.postgres'

    @classmethod
    def configure(cls):
        super(WhenRemovingDatabases, cls).configure()
        cls.db_object = compat.mock.Mock()
        cls.temp_db_list = cls.create_patch(
            '_temporary_databases', new_callable=list)
        cls.temp_db_list.append(cls.db_object)

    @classmethod
    def execute(cls):
        postgres._remove_databases()

    def should_drop_databases(self):
        self.db_object.drop.assert_called_once_with()

    def should_clear_list(self):
        self.assertEqual(postgres._temporary_databases, [])


class WhenDatabaseRemovalFails(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.postgres'

    @classmethod
    def configure(cls):
        super(WhenDatabaseRemovalFails, cls).configure()
        cls.db_object = compat.mock.Mock()
        cls.db_object.drop.side_effect = psycopg2.OperationalError

        cls.temp_db_list = cls.create_patch(
            '_temporary_databases', new_callable=list)
        cls.temp_db_list.append(cls.db_object)
        cls.logger = cls.create_patch('_logger')

    @classmethod
    def execute(cls):
        postgres._remove_databases()

    def should_log_failure(self):
        self.logger.exception.assert_called_once_with(
            compat.mock.ANY, self.db_object.connection_parameters)

    def should_still_clear_list(self):
        self.assertEqual(postgres._temporary_databases, [])


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


class WhenDroppingUncreatedDatabase(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenDroppingUncreatedDatabase, cls).configure()
        cls.db_object = postgres.TemporaryDatabase()
        cls.db_object._run_ddl = compat.mock.Mock()

    @classmethod
    def execute(cls):
        cls.db_object.drop()

    def should_not_run_ddl(self):
        self.assertFalse(self.db_object._run_ddl.called)
