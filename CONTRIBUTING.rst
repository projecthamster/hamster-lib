============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://projecthamster.atlassian.net/secure/CreateIssue!default.jspa.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

'hamster-lib' could always use more documentation, whether as part of the
official 'hamster-lib' docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://projecthamster.atlassian.net/secure/CreateIssue!default.jspa.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `hamster-lib` for local development.

1. Fork the `hamster-lib` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:projecthamster/hamster-lib.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed,
   this is how you set up your fork for local development. It will also take care of
   installing all packes required for a dev environment::

    $ mkvirtualenv hamster-lib
    $ cd hamster-lib/
    $ make develop
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests,
   including testing other Python versions with tox::

    $ make test-all

   For your intermediate quick-and-dirty testruns that include just the unittests, run::

     $ make test

   If you just want to check against a specific python (``py27`` or ``py34``) version, run::

     $ tox -e py27

   or::

     $ tox -e py34


6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests. Preferably they will not lower the total
   test coverage of the project.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7 and 3.4. Check `Travis
   <https://travis-ci.org/projecthamster/hamster-lib/builds/142418469>`_
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

    $ python -m unittest tests.test_hamster_lib
