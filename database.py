from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from config import settings

# The string form of the URL is
#     ``dialect[+driver]://user:password@host/dbname[?key=value..]``, where
#     ``dialect`` is a database name such as ``mysql``, ``oracle``,
#     ``postgresql``, etc., and ``driver`` the name of a DBAPI, such as
#     ``psycopg2``, ``pyodbc``, ``cx_oracle`
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/chat"
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# The Engine in SQLAlchemy is responsible for managing database connections, executing SQL statements,
#  and handling low-level database interactions.

# echo=True enables detailed logging of SQl statements executed
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# commit means pushing changes to database
# flush means syncing with DB, so that the changes not yet committed will still be
# visible when querying the DB, flush means copying changes to DB transaction buffer, but
# actual DB statements are not triggered, in commit they are triggered
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# this Base class will be used to create sqlalchemy models i.e. all
# sqlalchemy models will inherit this class
Base = declarative_base()


# added below to track creation of sessions

open_sessions = list()

@event.listens_for(SessionLocal, 'after_begin')
def receive_after_begin(session, transaction, connection):
    open_sessions.append(session)

@event.listens_for(SessionLocal, 'after_commit')
@event.listens_for(SessionLocal, 'after_rollback')
def receive_after_commit_or_rollback(session):
    open_sessions.remove(session)

# List of all open sessions
print("****************", open_sessions)
