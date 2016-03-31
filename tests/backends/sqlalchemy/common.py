from sqlalchemy import orm
Session = orm.scoped_session(orm.sessionmaker())
