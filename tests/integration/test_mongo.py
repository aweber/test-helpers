from __future__ import absolute_import

import os

from pymongo import MongoClient

from test_helpers import bases, mixins, mongo


class WhenCreatingTemporaryDatabase(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabase, cls).configure()
        cls.database = mongo.TemporaryDatabase(host='localhost', port='27017')

    @classmethod
    def execute(cls):
        cls.database.create()

    def should_create_database(self):
        mongodb = MongoClient(host='localhost', port=27017)
        self.assertIn(self.database.database_name, mongodb.database_names())


class WhenDroppingTemporaryDatabase(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenDroppingTemporaryDatabase, cls).configure()
        cls.database = mongo.TemporaryDatabase(host='localhost', port='27017')
        cls.database.create()

    @classmethod
    def execute(cls):
        cls.database.drop()

    def should_drop_database(self):
        mongodb = MongoClient(host='localhost', port=27017)
        self.assertNotIn(self.database.database_name, mongodb.database_names())


class WhenCreatingTemporaryDatabaseAndExportingEnv(
        mixins.EnvironmentMixin, bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabaseAndExportingEnv, cls).configure()
        cls.unset_environment_variable('MONGOHOST')
        cls.unset_environment_variable('MONGOPORT')
        cls.unset_environment_variable('MONGODATABASE')
        cls.database = mongo.TemporaryDatabase(host='localhost', port='27017')
        cls.database.create()

    @classmethod
    def execute(cls):
        cls.database.set_environment()

    def should_export_mongohost(self):
        self.assertEqual(os.environ['MONGOHOST'], self.database.host)

    def should_export_mongoport(self):
        self.assertEqual(os.environ['MONGOPORT'], str(self.database.port))

    def should_export_mongodatabase(self):
        self.assertEqual(os.environ['MONGODATABASE'], self.database.database_name)
