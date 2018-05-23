.. _tutorial:

Tutorial
=========

In this section we present examples of setting up tests for workflow
managers. The examples start out from a simple setting adding
complexity with each subsection. The tests and example workflow files
can be found in the tests directory that ships with the package
distribution.


Snakemake workflow
-------------------

This section describes how to setup tests of a snakemake workflow. In
order to use the test fixtures with the `snakemake workflow manager
<http://snakemake.readthedocs.io/en/stable/>`_, we need to setup a
Snakefile and a test file.

The Snakefile defines rules that declare what to do with the input
data. In a real-life scenario, we would run various bioinformatics
applications to transform the input into some meaningful output. Here,
we perform operations using basic shell commands, but the same
principle applies to a bioinformatics workflow. The Snakefile in this
example looks as follows:


.. literalinclude:: ../pytest_ngsfixtures/tests/Snakefile
   :language: python


Setting up a workflow with a predefined sample layout
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The test file `test_workflow_simple.py` defines a test `test_workflow`
that depends on the default
:py:data:`~pytest_ngsfixtures.plugin.samples` fixture. As the
Snakefile resides in the same directory, the
:py:data:`~pytest_ngsfixtures.wm.snakemake.snakefile` fixture will
automatically detect its presence and setup the file. If there is no
Snakefile present, the full path has to be passed with the `snakefile`
argument to `pytest.mark.snakefile`.

By default, fixtures are setup to copy files to the test directory. By
passing `copy=False` to the `pytest.mark` helpers, we use symlinks
instead. In addition, we pass the option `numbered=True` to generate
numbered output directories.

.. literalinclude::
                    ../pytest_ngsfixtures/tests/test_workflow_simple.py
   :language: python

The :py:func:`test_workflow` function requires the two fixtures
`samples` and `snakefile`, and the workflow is run with the
:py:func:`~pytest_ngsfixtures.snakemake.run` wrapper. Finally, we
assert that the test has run to completion by asserting the existence
of the output file `results.txt`. Now, the tests can be run with the
command

.. code-block:: shell

   pytest -v -s tests/test_workflow_simple.py


Setting up a docker container fixture
+++++++++++++++++++++++++++++++++++++

In the following test script (`test_workflow_docker.py`), we
add functionality to deal with container-based fixtures.

First, we import the :py:mod:`docker` module to interact with docker,
along with :py:mod:`os` and :py:mod:`pytest`:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 2-4

Then, we add a `container` fixture that sets up a container based on
the snakemake docker image
`quay.io/biocontainers/snakemake:X.Y.Z--py36_0
<https://quay.io/repository/biocontainers/snakemake?tag=latest&tab=tags>`_,
where `X.Y.Z` corresponds to the installed snakemake version:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 8-33

Finally, we add the `container` fixture to the test function call:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 36-45

and run the test as 

.. code-block:: shell

   pytest -v -s tests/test_workflow_docker.py



Parametrized tests on running environment
++++++++++++++++++++++++++++++++++++++++++

We have now written tests for local execution and execution in a
container. By parametrizing the tests, we can combine the two cases in
one test function. To do this we modify the test function as follows
(see `test_workflow_parametrize.py`):

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_parametrize.py
   :language: python
   :lines: 38-49

The parametrization is done indirectly via the `container` fixture. We
modify this fixture to return `None` if the request parameter equals
`local`, and if the parameter equals `docker` we return the container:


.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_parametrize.py
   :language: python
   :lines: 8-35

Now, running

.. code-block:: shell

   pytest -v -s tests/test_workflow_parametrize.py

will execute two tests, one for the local environment, one in the
docker container.
