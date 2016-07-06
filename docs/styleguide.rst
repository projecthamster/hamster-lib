General
=======

.. class:: compact

* Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ and
  `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_.
* Try to stick to 79 chars. When this is not enough you may use up to 99 chars.
  This is more tolerable for code than for documentation.
* Use double quotes for human readable strings and single quotes for all other strings.
* Private functions and methods are prefixed with a single underscore: ``_method``.

Python 2 and 3 compability
---------------------------

.. class:: compact

* Declare encoding in first line: ``-*- encoding: utf-8 -*-``
* Use *absolute_import* and *unicode_literals* from the ``__future__`` package.
* Use *six.text_type* to cast a unicode string under python 2 and 3.

Code-style
--------------
* Readability trumps almost anything. Readable and approachable code carries
  it's weight as a lower contribution-barrier, less bugs and easier
  debugging.  Having a particular clever, aka dense, alternative is rarely
  warranted.
* Favour multiple small specialized (local) functions/methods over big
  all-encompassing ones.
* Use well established and maintained high quality 3rd party libraries over own
  implementations.
* Use expressive variable names. If you have to trade off verbosity and
  expressiveness, go for the later.
* Assigning variables even if they are used only once can be preferable if
  expressions become clearer and less dense.
* Any method / function that is not deliberately considered part of the public
  API should be considered private. This is to increase the mental threshold
  for declaring them public as well as making it easier to the occasional
  reader to figure out which parts of the code are relevant to his/her needs
  and which are internal details.
* Try to minimize use of return statements with a method/function while using
  exceptions wherever suitable.  While this may not allways improve readability
  it tends to make debugging easier as it provides one central breaking point.
* Methods should have the following order: special (``__foo__``) > public  >
  private (`_foo``).

Imports
-------

.. class:: compact

* Imports should be grouped in the following order:

    * standard library imports
    * related third party imports
    * local application/library specific imports

* You should put a blank line between each group of imports.
* Always order each group of imports by name.
* You can use `isort <https://github.com/timothycrosley/isort>`_ to sort the
  imports.
* Remove import statements that are no longer used when you change code.

Documentation
---------------

.. class:: compact

* Docstrings should be provided for all public and private classes, methods and
  functions. Simple local functions may go without. They should elaborate the
  methods signature and use.
* Use `google-style <http://www.sphinx-doc.org/en/stable/ext/example_google.html#example-google>`_
  docstrings. Sphinx's `napoleon <http://www.sphinx-doc.org/en/stable/ext/napoleon.html#module-sphinx.ext.napoleon>`_
  extension will make turn this into valid ``rst``.
* use block comments to explain implementation

Committing and commit messages
------------------------------

.. class:: compact

* Commit one change/feature at a time (you can use `tig <http://jonas.nitro.dk/tig/>`_
  to select the changes you want to commit).
* Separate bug fixes from feature changes, bugfixes may need to be backported
  to the stable branch.
* Maximum line length is 50 characters for the first line and 72 for all
  following lines.
* The first line is a short summary, no trailing period.
* Leave a blank line between the summary and the body of the commit message.
* Explain what you did and add all relevant information to the commit message.
* If an issue exists for your feature/bug/task add it to the end of the commit
  message.
* Run the test suite **before** pushing your changes.
* **Never commit** passwords, ``*.pyc`` files, sqlite database files or ``pdb`` calls.

Rebasing
--------

.. class:: compact

* try to rebase to keep the commit history linear:

::

    $ git pull --rebase

* If you have uncommitted changes in your working directory use ``git stash`` to stash the changes while rebasing:

::

    $ git stash
    $ git pull --rebase
    $ git stash pop

* **Do not** rebase already published changesets!

Pull Requests
-------------

.. class:: compact

The title of a pull request should contain a summary of the issue it is related
to, as well as the issue id. An example would look like
``Advanced report options (#23)``. This way, a link between the PR and the
issue will be created.

Every pull request has to be approved by at least one other developer before
merging.
