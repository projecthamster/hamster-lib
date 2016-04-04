========
Usage
========

To use hamsterlib in a project::

    import hamsterlib

The main point of entry is ``hamsterlib.HamsterControl``. Your friendly timetracking
controler. All that is required to initialize it is that you pass it a ``dict`` with basic
configuration information. Right now, all that is needed are the following key/value
pairs::

        'work_dir': ``path``; Where to store any temporary data
        'store': 'sqlalchemy'; refer to ``hamsterlib.lib.REGISTERED_BACKENDS``
        'db_path': ``sqlalchemy db path``,
        'tmpfile_name': filename; under which any 'ongoing fact' will be saved

``hamsterlib.HamsterControl`` initializes the store and provides a general logger.
Besides that ``HamsterControl.categories``, ``HamsterControl.activities`` and 
``HamsterControl.facts`` are the main interfaces to communicate with the storage backend.

Besides this general controler ``hamsterlib.helpers`` provides convinience functions
that help with normalization and general intermediate computation clients may have need
for.

This documentation need to be expanded, but hopefully it is enough for now to get 
you started. For detail please see the module reference and tests.



        
