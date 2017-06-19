.. :changelog:

History
=======

0.13.1 (2017-06-19)
--------------------
* Remove check for ``start`` info when validating timeframes with with
  ``helpers.time.validate_start_end_range``. [LIB-250]

0.13.0 (2017-06-07)
--------------------
* ``helpers.time.extract_time_info`` checks that ``end > start``. [LIB-30]
* Some attributes of the internal ``XMLWriter`` class have been renamed. [LIB-109]
* ``stop_tmp_fact`` now accepts hints about the end (date-)time. [LIB-129]
* A new method ``update_tmp_fact`` has been added. [LIB-132]
* Added ``Fact.serialized_string``. [LIB-216]
* Raw fact parsing has been moved to a separate helper method. [LIB-230]
* Added backend related config helpers. [LIB-235]
* We now use the built-in ``configparser`` module under python 3. [LIB-236]

0.12.0 (2016-08-05)
--------------------
* Added support for tags! ``hamster_lib.objects.Tag`` instances can be appended
  to ``Fact.tags`` and will be stored by the sqlalchemy backend. We also
  provide comprehensive CRUD methods as part of the brand new
  ``storage.TagManager``.
* Major refactoring of *raw fact* parsing. In particular the way timeinfo is
  extracted from the string. We are now very clear and explicit about the
  supported timeinfo formats. Anything unmatched before the ``@`` token will be
  considered the ``activity.name``. This means in particular that our activity
  names may contain whitespace!
* Added new ``partial`` parameter to ``time.complete_timeframe`` which defaults
  to ``False`` which maintains the functions previous behaviour. Setting it to
  ``True`` however will cause it to only 'complete' those bits of the timeframe
  where there is at least some partial (time or date) information available.
* Moved time related helpers to a dedicated submodule:
  ``hamster_lib.helpers.time``
* Added ``HamsterControl.update_config`` method to allow config updates at
  runtime.
* Renamed ``get_config`` helper to ``load_config`` and limit it to deal just
  with config retrieval. It no longer ensures a default config is written and
  returned. Your client will need to handle any such fallback behaviour now.
* Use ``tox-travis`` to ensure proper multi python version testing on Travis-CI
* Minor fixes in ``config_helpers._get_config_instance``
* Renamed requirements/\*.txt to \*.pip

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
