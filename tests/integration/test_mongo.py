from __future__ import absolute_import

from pymongo import MongoClient

from test_helpers import bases, mixins, mongo


class WhenCreatingTemporaryDatabase(bases.BaseTest):

    @classmethod
    def configure(cls):
        super(WhenCreatingTemporaryDatabase, cls).configure()
        cls.database = mongo.TemporaryDatabase(host='localhost', port=27017)

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
        cls.database = mongo.TemporaryDatabase(host='localhost', port=27017)
        cls.database.create()

    @classmethod
    def execute(cls):
        cls.database.drop()

    def should_drop_database(self):
        mongodb = MongoClient(host='localhost', port=27017)
        self.assertNotIn(self.database.database_name, mongodb.database_names())
