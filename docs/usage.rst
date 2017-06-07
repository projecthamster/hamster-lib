========
Usage
========

To use hamsterlib in a project::

    import hamsterlib

The main point of entry is ``hamsterlib.HamsterControl``. Your friendly timetracking
controller. All that is required to initialize it is that you pass it a ``dict`` with basic
configuration information. Right now, all that is needed are the following key/value
pairs::

        'work_dir': ``path``; Where to store any temporary data
        'store': 'sqlalchemy'; refer to ``hamsterlib.lib.REGISTERED_BACKENDS``
        'db_path': ``sqlalchemy db path``,
        'tmpfile_name': filename; under which any 'ongoing fact' will be saved
        'fact_min_delta': integer; Amount of seconds under which fact creation will be prohibited.

``hamsterlib.HamsterControl`` initializes the store and provides a general
logger. Besides that ``HamsterControl.categories``,
``HamsterControl.activities`` and ``HamsterControl.facts`` are the main
interfaces to communicate with the storage backend.

The second cornerstone are the dedicated classes ``Category``, ``Activity`` and
``Fact`` which, for convinience, can be imported right from ``hamsterlib``. In
particular ``Fact.create_from_raw_fact`` might be of insterest They provide
easy and consistent facilities to create, store and manage data relevant to
your timetracking needs. Of particular interest is
``hamsterlib.Fact.create_from_raw`` which allows you to pass a ``raw_fact``
string and reciceve a fully populated ``Fact`` instance in return. The class
will take care of all the tedious parsing and normalizing of data present in
the ``raw_fact``.

For clients aiming to utilize the new and sanitized backend API a look into
``hamsterlib.storage`` may be worthwile. These classes describe our baseline
API that is to be implemented by any valid backend of ours. Note that some
general methods are provided on this level already, so backend developers don't
have to each time anew.  Of cause they are always free to overload them in
order to implement solutions optimized to their concrete backend
infrastructure.

Besides this general controller ``hamsterlib.helpers`` provides convenience
functions that help with normalization and general intermediate computation
clients may have need for.

Basic Terminology
------------------

The following is intended as a rough description of the basic semantics of terminology used
as part of this project. For technical details please refer to the module reference, in
particular ``hamsterlib.objects``.

Category
   What it says on the tin. A user friendly way to group accitities that
   relate to each other. Their names are unique.

Activity
   'What you are doing'. This is a brief and easy to remember describtion of
   the (you guessed it) 'activity' you want to track. An *activity* can be
   filed under a category in order to provide some structure or just stay
   *uncategrized*.  While one 'activity name' can be used with multiple
   *categories* it will be considered as a different thing all together as far
   as we are concerned. E.g. an activity called 'meeting' filed under the
   'private' category will be absolutly seperate from an activity named
   'meeting' filed under 'bussiness'. Within each *category*, activitynames
   will be unique.

Fact
   An actually timetracked activity. That is, an entry about 'what did you do
   from start to end'. As such it connects an general *Activity* with
   timetracking information as well as additional optional context infos (tags
   and description).  A *fact* is usually what you are ultimativly interested
   in. What shows up in your report and allows you to see what you did when.

Ongoing fact
   Legacy hamster allowed for facts without an end to be saved to the database.
   We do not. However, to address the common use case that a client may want to
   start tracking an activity, but does not know its end, we provide a
   convinient solution so clients don't have to implement this each by anew.
   We provide an API for creating one and only one persistent *ongoing fact*. A
   fact without specified end. This fact is treated seperatly the others in
   almost any regard internaly.  As far as the client is concerned it is
   however just a regular fact without specified end.  Fact manager methods
   relevant to this carry ``tmp_fact`` in their name.

This documentation need to be expanded, but hopefully it is enough for now to
get you started. For detail please see the module reference and tests.


Assumptions and Premisses
--------------------------
As any software, we make assumptions and work on premises. Here we try to make
them transparent.

* There can be only one fact any given point in time. We do not support
  multiple concurrent facts.




