import atexit
import datetime
import logging
import os
import uuid

from pymongo import MongoClient

_logger = logging.getLogger(__name__)
_temporary_databases = []


def _remove_databases():
    for db in _temporary_databases:
        try:
            db.drop()
        except:
            _logger.exception('failed to drop mongo database %r',
                              db.database_name)
    del _temporary_databases[:]

atexit.register(_remove_databases)


class TemporaryDatabase(object):
    """
    Creates a temporary MongoDB database that is destroyed automatically.

    :keyword str host: Database to connect to. This defaults to
        :envvar: ``MONGOHOST`` or ``localhost`` if omitted.
    :keyword int port: Port number that the database is listening on. This
        defaults to :envvar: ``MONGOPORT` or ``27017`` if omitted.

    Instances of this class will create a bare MongoDB database with a single
    collection named ``test_helpers`` containing a single document with a
    create date for tracking purposes. When the test process exits all
    databases created will be destroyed automatically. Under the hood it uses
    ``pymongo`` and registers a single cleanup function with
    :func`atexit.register`.

    **Usage Example**

    .. code-block:: python

       from test_helpers import mongo

       _testing_db = mongo.TemporaryDatabase()

       def setup_module():
           _testing_db.create()
    """

    def __init__(self, **kwargs):
        super(TemporaryDatabase, self).__init__()
        self.host = kwargs.pop('host',
                               os.environ.get('MONGOHOST', 'localhost'))
        self.port = int(kwargs.pop('port', os.environ.get('MONGOPORT', 27017)))
        self.database_name = None

    def create(self):
        """Create the temporary database if it does not exist."""

        if self.database_name is not None:
            return
        database_name = 'test{0}'.format(uuid.uuid4().hex)

        mongodb = MongoClient(self.host, self.port)
        db = mongodb[database_name]
        collection = db['test_helpers']
        collection.insert({'create_date': datetime.datetime.utcnow()})

        self.database_name = database_name
        _temporary_databases.append(self)

    def drop(self):
        """Drop the temporary database if it was created."""
        if self.database_name is None:
            return
        mongodb = MongoClient(self.host, self.port)
        mongodb.drop_database(self.database_name)
        _temporary_databases.remove(self)
        self.database_name = None

    def set_environment(self):
        """
        Export MongoDB environment variables for the database.

        This exports the :envvar:`MONGOHOST`, :envvar:`MONGOPORT`, and
        :envvar:`MONGODATABASE` environment variables

        """
        os.environ['MONGOHOST'] = self.host
        os.environ['MONGOPORT'] = str(self.port)
        if self.database_name is not None:
            os.environ['MONGODATABASE'] = self.database_name
