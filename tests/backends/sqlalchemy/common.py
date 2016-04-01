from sqlalchemy import orm

"""
Provide a central global Session-object.

This way it can be referencecd by fixtures and factories.
[Details](http://factoryboy.readthedocs.org/en/latest/orms.html#sqlalchemy)
"""

Session = orm.scoped_session(orm.sessionmaker())
