.. :changelog:

History
=======

0.11.0 (2016-07-06)
--------------------
* Renamed this package to ``hamster-lib`` as it now an offical part of
  `projecthamster <https://github.com/projecthamster>`_. It was previously
  named and distributed as `hamsterlib <https://pypi.python.org/pypi/hamsterlib/0.1.0>`_
* Add documentation checker ``pep257`` to testsuite.
* Fixed docstrings.
* Removed ``hamster_lib.objects.Fact.serialized_name``.
* Improved test factories
* Made ``hamster_lib.objects.*`` *hashable*.
* Provide consistent and improved ``__repr__`` methods for
  ``hamster_lib.objects`` classes.
* ``FactManager._get_all`` can now return facts completely*or* partially within
  the timeframe. As a consequence, we removed
  ``FactManager._timeframe_is_free``.
* Added a set of helper function to ease common configuration related tasks.
  In particular they make it easy to store a given config at its canonical
  file system location.
* Improved ``ActivityManager.get_all`` to enable it to return *all* activities.

0.10.0 (2016-04-20)
-------------------
* Add ``ical`` export facilities. Brand new writer using the ``icalendar`` library.
* Add ``xml`` export facilities.
* Switch to `semantic versioning <http://semver.org>`_
* Added GPL3 boilerplate
* Provide documentation on packaging and ``requirements.txt``.
* Add support for `editorconfig <http://editorconfig.org>`_
* Introduce fine grained, storage backend dependent config options.

0.0.3 (2016-04-08)
-------------------
* fact managers ``save`` method now enforces new ``fact_min_delta`` setting.
* Fixed broken packing in ``setup.py``.
* Storage manager methods now use extensive logging.
* Documentation moved to 'alabaster' theme and content extended.
* Remove usage of ``future.builtins.str``.
* Adjusted ``release`` make target.

0.0.2 (2016-04-07)
------------------
* First release on PyPi
* Improved documentation
* Support for *ongoing facts*.
* Updated requirements

0.0.1 (2016-04-03)
---------------------
* First release on github
