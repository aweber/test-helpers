import pymongo

from test_helpers import bases, compat, mixins, mongo


class WhenRemovingDatabases(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.mongo'

    @classmethod
    def configure(cls):
        super(WhenRemovingDatabases, cls).configure()
        cls.db_object = compat.mock.Mock()
        cls.temp_db_list = cls.create_patch(
            '_temporary_databases', new_callable=list)
        cls.temp_db_list.append(cls.db_object)

    @classmethod
    def execute(cls):
        mongo._remove_databases()

    def should_drop_databases(self):
        self.db_object.drop.assert_called_once_with()

    def should_clear_variable(self):
        self.assertEqual(mongo._temporary_databases, [])


class WhenDatabaseRemovalFails(mixins.PatchMixin, bases.BaseTest):
    patch_prefix = 'test_helpers.mongo'

    @classmethod
    def configure(cls):
        super(WhenDatabaseRemovalFails, cls).configure()
        cls.db_object = compat.mock.Mock()
        cls.db_object.drop.side_effect = pymongo.errors.InvalidOperation

        cls.temp_db_list = cls.create_patch(
            '_temporary_databases', new_callable=list)
        cls.temp_db_list.append(cls.db_object)
        cls.logger = cls.create_patch('_logger')

    @classmethod
    def execute(cls):
        mongo._remove_databases()

    def should_log_failure(self):
        self.logger.exception.assert_called_once_with(
            compat.mock.ANY, self.db_object.database_name)

    def should_still_clear_list(self):
        self.assertEqual(mongo._temporary_databases, [])
