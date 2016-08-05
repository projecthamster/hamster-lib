Notes
=====

These notes are just a dumping ground for semanitic information extracted from
legacy hamster while dealing with its codebase that is not documented/obvious.
Also, some basic troubleshooting heuristics and 'lessons learned' may be
documented here for now.

* Why all this buisiness with ``search_names``, which are lowercase versions of
  proper names?  Is it because cases insesitive matching was not available? or
  due to performence considerations?

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

  after we started using factory-instance fixtures 'alchemy_category' vs
  'alchemy_category_factory'


* Integrity Error (SQLAlchemy)
  If we end up with 'constraint` or 'Integrety' erros although we should not have commited
  anything to the db, it may be that one of our unsuspicious queries nearby triggered an
  autoflush/commit.
  Popular candidates are lookup- and count queries.
  One way to get around this using instances of classes not tracked/mapped by SQLAlchemy.

Not supported legacy 'functionality'
---------------------------------------
Not now:

* ``search_name``
* indexing
* ical export
* autocomplete
* ``resurrect``/``temporary`` mechanic
* ``get facts`` can inverse search_terms
* trophies
* migration from old database aka ``run_fixtures``.

Opted against:

* ``__solve_overlaps``
* ``__squeeze_in``
* ``__touch_fact)``


Legacy Storage API notes
------------------------
* ``get_tag_ids`` seems to create tags that have been passed if they do not
  exist * activities flagged as ``temporary`` dont get ressurected
  (``__add_fact``).
* seperate ``storage.__get_activities`` is dedicated to autocomplete. we
  summerized its usecase under the regular one so far.  The difference seems to
  be that autocomplete reasonable needs a way to retrieve *all* activity names,
  irrespective of category association. This should be coverable by adding a
  ``categories=False`` flag to our default method. Worth noting: considers only
  non-deleted activities. Activities are returned ordered by their
  corresponding facts start time with the 'latests' beeing first. Maybe it is
  actually cleaner to add a dedicated method like this once we get to
  autocomplete.

Dismissed:

* resurrect/temporary for ``add_fact`` is about checking for preexisting
  activities by using ``__get_activity_by_name``. If True we will consider
  'deleted' activities and stick this to our new fact.

  * We don't do temporary facts.

* if an activity is created with ``temporary=True`` it will be marked as
  ``deleted=True``.  why not set the attribute directly? Whats the role of a
  temporary activity?

  * This is only used when creating *temporary facts* in order to prevent
    proper activities beeing created for them. We don't do temporary facts, so
    we can ommit this.

Things we try to improve
------------------------

* python >=2.7, >=3.4 support
* full unicode support
* full pep8 and 257 complience
* >=95% test coverage
* strict and honest *seperation of concerns*. We provide just the backend, but
  that we do proper.  * cleaner, more object oriented pythonic code
* 'one exit point' strategy for method return values. Reduce the spagettiness.
* modular architecture.
* focus on solid core functionality and only expand features once existing code
  meets our standart.
* better project layout including waffle.io, codeship.com and requirements.io
* fully integrated and focused on PyPi distribution. All you need for
  production, test or dev comes out of the box with regular python tools.

