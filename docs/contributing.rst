..
   .. include:: ../CONTRIBUTING.rst

Developer guide
===============

Summary
----------

Development is based on `Vincent Driessen's branching model`_, with a
stable master branch and active develop branch. Use the issue tracker
to submit bug reports and post feature requests. Please submit pull
requests via separate feature branches.

Setting up a local copy
-------------------------

See installation section :ref:`installation-from-sources`.


Adding new application data
----------------------------

`pytest-ngsfixtures` is bundled with application data from a variety
of bioinformatics programs. The data is primarily used in test-based
development, even though a beneficial side-effect is that the data can
be used in unit tests.

Application output data is automatically generated using Snakemake in
order to track data provenance. However, adding new application data
is a time-consuming process. To speed up addition of new applications,
there is as of version 0.4.0 a script
`pytest_ngsfixtures_add_application.py` that aids in setting up the
necessary Snakefiles and configuration files for generating
application data.

The script will automatically setup a feature branch based on
*develop* and add template files. Running the script in dry mode with
a bogus application *foo* as argument gives the following output:

.. code-block:: console


   DRY RUN: cd /home/user/dev/pytest-ngsfixtures/pytest_ngsfixtures/data/applications
   DRY RUN: git checkout develop
   DRY RUN: git checkout -b feature/application/foo
   DRY RUN: setup new application directory /home/user/dev/pytest-ngsfixtures/pytest_ngsfixtures/data/applications/foo
   DRY RUN: saving /home/user/dev/pytest-ngsfixtures/pytest_ngsfixtures/data/applications/foo/config.yaml and /home/user/dev/pytest-ngsfixtures/pytest_ngsfixtures/data/applications/foo/Snakefile

   All set to go!

   1. cd to /home/user/dev/pytest-ngsfixtures/pytest_ngsfixtures/data/applications/foo
   2. Start adding rules to Snakefile and modify config.yaml accordingly
   3. run 'snakemake conda' to generate conda files
   4. run 'snakemake --use-conda all' to generate output
   5. (optional): run 'snakemake clean' to remove excess output
   6. run 'git add Snakefile config.yaml FILENAMES' to add output
   7. submit pull request to https://github.com/percyfal/pytest-ngsfixtures
		

.. _Vincent Driessen's branching model: http://nvie.com/posts/a-successful-git-branching-model/
