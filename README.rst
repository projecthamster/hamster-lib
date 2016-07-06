===============================
hamsterlib
===============================

.. image:: https://img.shields.io/travis/projecthamster/hamster-lib/master.svg
        :target: https://travis-ci.org/projecthamster/hamster_lib

.. image:: https://img.shields.io/codecov/c/github/projecthamster/hamster-lib/master.svg
        :target: https://codecov.io/github/projecthamster/hamster-lib

.. image:: https://readthedocs.org/projects/hamster-lib/badge/?version=master
        :target: http://hamster-lib.docs.projecthamster.org/en/latest/
        :alt: Documentation Status

.. image:: https://requires.io/github/projecthamster/hamster-lib/requirements.svg?branch=master
        :target: https://requires.io/github/projecthamster/hamster-lib/requirements/?branch=master
        :alt: Requirements Status

(A badges refer to ``master``)

A library for common timetracking functionality.

``hamster-lib`` aims to be a replacement for ``projecthamster``  backend
library.  While we are not able to function as a  straight forward drop-in
replacement we try very hard to stay as compatible as possible. As a
consequence clients are able to switch to ``hamster-lib``  merely by changing
some basic calls. Most of the semantics and return values will be as before.

This itself points to a major architectural shift in the way ``hamster-lib``
approaches timetracking. We are firm believers in *do one thing, and do it
well*. The tried and tested unix toolbox principle. As such we focus on
providing useful backend functionality and helper methods so clients (dbus
interfaces, CLIs or graphical UIs) can build upon a solid and consistent base
and focus on their specific requirements.

Features
--------
* Full python >=2.7 and >=3.4 compatibility
* Full unicode support
* >= 95% test coverage
* Extensive documentation
* Focus on clean, maintainable code.
* Free software: GPL3
* All you need for production, test or dev environments comes out of the box
  with regular python tools.

First Steps
-----------
* Build dev environment: ``make develop``
* Build the documentation locally: ``make docs``
* Run just the tests: ``make test``
* Run entire test suite including linters and coverage: ``make test-all``

Additional Resources
--------------------
* `Documentation by 'read the docs' <http://hamster-lib.docs.projecthamster.org/en/latest>`_
* `CI thanks to Travis-CI <https://travis-ci.org/projecthamster/hamster-lib>`_
* `Coverage reports by 'codecov' <https://codecov.io/gh/projecthamster/hamster-lib>`_
* `Dependency monitoring by 'requires.io' <https://requires.io/github/projecthamster/hamster-lib/requirements/?branch=master>`_

News: Version 0.11.0
---------------------
This is the first release of ``hamster-lib`` as official part of
`projecthamster <https://github.com/projecthamster>`_.
As such it includes a lot of internal adjustments and minor fixes.
Besides such housekeeping however, is also offers some genuine new features.
You can now query ``ActivityManaget.get_all`` to return *all* activities, where
it previously only returned *all for given category*. We also made
``Category``, ``Activity`` and ``Fact`` hashable, so you can now use them as
``dict`` keys or ``set`` elements.
For a more detailed overview about what new, please refer to the changelog.
Happy tracking; Eric.

Todo
----
This early release is mainly meant as a rough proof-of-concept at this stage.
It showcases our API as well as our general design decisions.  As such there
are a few functionalities/details of the original ``projecthamster`` backend
that we wish to allow for, but are not provided so far.  These are:

* Tags (We accept them but they are not stored in the backend.)
* Autocomplete related methods
* Trophies (The jury is still out on if and how we want to support those.)
* Migrations from old databases.

Incompatibilities
------------------
Despite our efforts to stay backwards compatible we did deliberately break the
way ``Facts`` without end dates are handled. We think allowing for them in any
persistent backend creates a data consistency nightmare and so far there seems
no conceivable use case for it, let alone an obvious semantic.  What we do
allow for is *one* ``ongoing fact``. That is a fact that has a start, but no
end date. For details, please refer to the documentation.

Credits
---------
Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
