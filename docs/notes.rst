====
Notes
====

These notes are just a dumping ground for semanitic information extracted from legacy hamster
while dealing with its codebase that is not documented/obvious. Also, some basic
troubleshooting heuristics and 'lessons learned' may be documented here for now.

* Names seem to be case sensitive. This should propably be documented properly with
  regards to search/filter.

* It looks like the dbus client assume PKs to be > 0 and uses 0 as marker for failure.
  Would be great if we can change that on the frontend instead of working around that.

* Whilst we do support networked/distributed storage acces we do not at all can
  provide multiple simultanious connections. Our backend uses the fact that an
  Object has a PK to decide if it updates or inserts. If any other "client" has
  manipulated the data stored under this key between this clients retrieval and
  its save call, those changes will simply be overwritten.


* force_flush on SQLAlchemy-factories helped with:


        sqlalchemy.exc.IntegrityError: (raised as a result of Query-invoked autoflush;
        consider using a session.no_autoflush block if this flush is occurring prematurely)
        (sqlite3.IntegrityError) UNIQUE constraint failed: categories.name
        [SQL: 'INSERT INTO categories (id, name) VALUES (?, ?)'] [parameters: ((19, 'vero'),
        (20, 'officiis'), (21, 'aliquid'), (22, 'vero'), (23, 'dolorum'))]

  after we started using factory-instance fixtures 'alchemy_category' vs 'alchemy_category_factory'


* Integrity Error (SQLAlchemy)
  If we end up with 'constraint` or 'Integrety' erros although we should not have commited
  anything to the db, it may be that one of our unsuspicious queries nearby triggered an
  autoflush/commit.
  Popular candidates are lookup- and count queries.
  One way to get around this using instances of classes not tracked/mapped by SQLAlchemy.

* resurrect/temporary for ``add_fact`` is about checking for preexisting activities
  by using ``__get_activity_by_name``. If True we will consider 'deleted' activities
  and stick this to our new fact.
