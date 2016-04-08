===============================
hamsterlib
===============================

.. image:: https://img.shields.io/pypi/v/hamsterlib.svg
        :target: https://pypi.python.org/pypi/hamsterlib

.. image:: https://img.shields.io/codeship/30ec8f70-dbc9-0133-f7bf-561c728b2028/master.svg
        :target: https://codeship.org/elbenfreund/hamsterlib

.. image:: https://img.shields.io/codecov/c/github/elbenfreund/hamsterlib/master.svg
        :target: https://codecov.io/github/elbenfreund/hamsterlib

.. image:: https://badge.waffle.io/elbenfreund/hamsterlib.svg?label=ready&title=Ready
        :target: https://waffle.io/elbenfreund/hamsterlib
        :alt: 'Stories in Ready' 

.. image:: https://readthedocs.org/projects/hamsterlib/badge/?version=master
        :target: https://readthedocs.org/projects/hamsterlib/?badge=master
        :alt: Documentation Status

.. image:: https://requires.io/github/elbenfreund/hamsterlib/requirements.svg?branch=master
        :target: https://requires.io/github/elbenfreund/hamsterlib/requirements/?branch=master
        :alt: Requirements Status

(A badges refer to ``master``)

A library for common timetracking functionality.

``hamsterlib`` aims to be a replacement for ``projecthamster``  backend
library.  While we are not able to function as a  straight forward drop-in
replacement we try very hard to stay as compatible as possible. As a consequence
clients are able to switch to ``hamsterlib``  merely by changing some basic 
calls. Most of the semantics and return values will be as before.

This itself points to a major architectural shift in the way ``hamsterlib`` approaches
timetracking. We are firm believers in *do one thing, and do it well*. The tried and
tested unix toolbox principle. As such we focus on providing useful backend
functionality and helper methods so clients (dbus interfaces, CLIs or graphical UIs)
can build upon a solid and consistent base and focus on their specific requirements.


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

.. _codeship: https://codeship.com

First Steps
-----------
* Build dev environment: ``make develop``
* Build the documentation locally: ``make docs``
* Run just the tests: ``make test``
* Run entire test suite including linters and coverage: ``make test-all``

Additional Resources
--------------------
* `Documentation by 'read the docs' <https://hamsterlib.readthedocs.org>`_
* `Project management with 'waffles' <https://waffle.io/elbenfreund/hamsterlib>`_
* `CI thanks to 'codeship' <https://codeship.com/elbenfreund/hamsterlib>`_
* `Coverage reports by 'codecov' <https://codecov.io/elbenfreund/hamsterlib>`_
* `Dependency monitoring by 'requires.io' <https://requires.io/github/elbenfreund/hamsterlib/requirements/?branch=master>`_

Todo
----
This early release is mainly meant as a rough proof-of-concept at this stage. It
showcases our API as well as our general design decisions.
As such there are a few functionalities/details of the original ``projecthamster``
backend that we wish to allow for, but are not provided so far.
These are:

* Tags (We accept them but they are not stored in the backend.)
* ical export
* Autocomplete related methods
* Trophies (The jury is still out on if and how we want to support those.)
* Migrations from old databases.

Incompatibilities
------------------
Despite our efforts to stay backwards compatible we did deliberately break the way
``Facts`` without end dates are handled. We think allowing for them in any persistent
backend creates a data consistency nightmare and so far there seems no conceivable
use case for it, let alone an obvious semantic.
What we do allow for is *one* ``ongoing fact``. That is a fact that has a start,
but no end date. For details, please refer to the documentation.

Credits
---------
Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
