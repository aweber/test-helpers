import atexit
import logging
import os
import uuid

import psycopg2


_logger = logging.getLogger(__name__)
_temporary_databases = []


def _remove_databases():
    for db in _temporary_databases:
        try:
            db.drop()
        except:
            _logger.exception(
                'failed to drop database %r', db.connection_parameters)
    del _temporary_databases[:]

atexit.register(_remove_databases)


class TemporaryDatabase(object):

    STARTING_DATABASE = 'postgres'
    """Database to connect to when cloning the template."""

    def __init__(self, **kwargs):
        super(TemporaryDatabase, self).__init__()
        self.user = kwargs.pop('user', os.environ.get('PGUSER', 'postgres'))
        self.password = kwargs.pop('password', None)
        self.host = kwargs.pop('host', os.environ.get('PGHOST', 'localhost'))
        self.port = kwargs.pop('port', os.environ.get('PGPORT', '5432'))
        self._connect_kwargs = kwargs
        self._database_name = None

    @property
    def connection_parameters(self):
        """Keyword parameters for :func:`psycopg2.connect`."""
        return {
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'port': self.port,
            'database': self._database_name,
        }

    def create(self, template='template0', **options):
        """
        Create the temporary database if it does not exist.

        :param str template: the name of the database to use as a
            template for the new database.  This defaults to
            ``template0`` if omitted.
        :keyword options: additional parameters to use in the
            ``CREATE DATABASE`` command.

        """
        if self._database_name is not None:
            return
        database_name = 'test{0}'.format(uuid.uuid4().hex)
        self._run_ddl(
            'CREATE DATABASE "{0}" TEMPLATE="{1}" {2}',
            database_name,
            template,
            ' '.join("{0}='{1}'".format(k, v) for k, v in options.items()),
        )
        self._database_name = database_name
        _temporary_databases.append(self)

    def drop(self):
        """Drop the temporary database if it was created."""
        if self._database_name is None:
            return
        self._run_ddl('DROP DATABASE IF EXISTS "{0}"', self._database_name)
        self._database_name = None

    def set_environment(self):
        """
        Export Postgres environment variables for the database.

        This exports the :envvar:`PGUSER`, :envvar:`PGHOST`,
        :envvar:`PGPORT`, and :envvar:`PGDATABASE` environment variables
        set to match :attr:`.connection_parameters`.

        """
        os.environ['PGUSER'] = self.user
        os.environ['PGHOST'] = self.host
        os.environ['PGPORT'] = str(self.port)
        if self._database_name is not None:
            os.environ['PGDATABASE'] = self._database_name

    def _run_ddl(self, ddl_stmt, *args):
        conn_params = self._connect_kwargs.copy()
        conn_params.update(self.connection_parameters)
        conn_params['database'] = self.STARTING_DATABASE
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        try:
            with conn.cursor() as cursor:
                sql = ddl_stmt.format(*args)
                _logger.debug('running DDL query - %s', sql)
                cursor.execute(sql)
        finally:
            conn.close()
