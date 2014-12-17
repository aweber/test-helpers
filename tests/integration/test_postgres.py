from __future__ import absolute_import

import os

import psycopg2

from test_helpers import bases, mixins, postgres


class WhenCreatingTemporaryDatabase(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabase, cls).configure()
        cls.database = postgres.TemporaryDatabase(
            host='localhost', user='postgres', password=None)

    @classmethod
    def execute(cls):
        cls.database.create()

    def should_create_database(self):
        conn = psycopg2.connect(**self.database.connection_parameters)
        conn.close()

    def should_save_database_information(self):
        self.assertIn(self.database, postgres._temporary_databases)


class WhenCreatingTemporaryDatabaseWithOptions(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabaseWithOptions, cls).configure()
        cls.database = postgres.TemporaryDatabase(
            host='localhost', user='postgres', password=None)

    @classmethod
    def execute(cls):
        cls.database.create(
            encoding='SQL_ASCII',
            lc_ctype='en_US.US-ASCII',
            lc_collate='en_US.US-ASCII',
        )

    def should_create_database_with_options(self):
        conn = psycopg2.connect(**self.database.connection_parameters)
        try:
            self.assertEqual(conn.encoding, 'SQLASCII')
        finally:
            conn.close()


class WhenCreatingTemporaryDatabaseWithoutParameters(
        mixins.EnvironmentMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabaseWithoutParameters, cls).configure()
        cls.set_environment_variable('PGHOST', 'somewhere.com')
        cls.set_environment_variable('PGUSER', 'someone')
        cls.set_environment_variable('PGPORT', '12345')

    @classmethod
    def execute(cls):
        cls.database = postgres.TemporaryDatabase()

    def should_use_environment_variables(self):
        self.assertEqual(
            self.database.connection_parameters,
            {
                'host': os.environ['PGHOST'],
                'port': os.environ['PGPORT'],
                'user': os.environ['PGUSER'],
                'password': None,
                'database': None,
            }
        )


class WhenCreatingTemporaryDatabaseWithoutParametersOrEnvVars(
        mixins.EnvironmentMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(
            WhenCreatingTemporaryDatabaseWithoutParametersOrEnvVars,
            cls).configure()
        cls.unset_environment_variable('PGHOST')
        cls.unset_environment_variable('PGUSER')
        cls.unset_environment_variable('PGPORT')

    @classmethod
    def execute(cls):
        cls.database = postgres.TemporaryDatabase()

    def should_use_default_values(self):
        self.assertEqual(
            self.database.connection_parameters,
            {
                'host': 'localhost',
                'port': '5432',
                'user': 'postgres',
                'password': None,
                'database': None,
            }
        )

