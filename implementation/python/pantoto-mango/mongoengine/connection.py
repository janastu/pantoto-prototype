from pymongo import Connection as MongoConnection
import settings

__all__ = ['ConnectionError', 'Connection']

class ConnectionError(Exception):
    pass

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance

class Connection(object):
    # This means we can connect to only one database, which shouldn't be a problem
    __metaclass__ = Singleton

    db_host = settings.MONGO_HOST
    db_port = int(settings.MONGO_PORT)
    db_name = settings.MONGO_DBNAME
    db_username = settings.MONGO_USERNAME
    __db_password = settings.MONGO_PASSWORD
    
    def __make_connection(self):
        """Connect to the database server if not already connected"""

        try:
            self.__connection
        except AttributeError:
            self.__connection = MongoConnection(Connection.db_host, Connection.db_port)

    def _get_db(self):
        """Connect to the database if not already connected"""

        if not Connection.db_name:
            raise ConnectionError('No database specified')

        self.__make_connection()

        try:
            self.__db
        except:
            # Get DB from current connection and authenticate if necessary
            self.__db = self.__connection[Connection.db_name]

        if self.db_username:
            self.__db.authenticate(Connection.db_username, Connection.__db_password)

        return self.__db

    def connect(self):
        """Connect to the database"""
        return self._get_db()
