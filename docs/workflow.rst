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

The test file (here `test_workflow_simple.py`) defines a test that
depends on the :py:data:`~pytest_ngsfixtures.plugin.flat`
pytest_ngsfixtures fixture:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_simple.py
   :language: python

Here, the Snakefile fixture is defined via the
:py:func:`~pytest_ngsfixtures.snakemake.snakefile_factory`. By
default, the factory will assume there is a Snakefile in the test
directory. If not, the full path to the Snakefile has to be passed
with the `snakefile` argument. The :py:func:`test_workflow` function
requires the two fixtures Snakefile and flat, and the workflow is run
with the :py:func:`~pytest_ngsfixtures.snakemake.run` wrapper.
Finally, we assert that the test has run to completion by asserting
the existence of the output file `results.txt`. Now, the tests can be
run with the command

.. code-block:: shell

   pytest -v -s test_workflow1.py



Setting up a workflow with a custom sample layout
++++++++++++++++++++++++++++++++++++++++++++++++++

The :py:data:`~pytest_ngsfixtures.plugin.flat` fixture is a predefined
fixture that sets up test files via symlinks. However, as will become
clear in the next section, sometimes it is desirable to copy the files
to the test directory.

We here use the :py:func:`~pytest_ngsfixtures.factories.sample_layout`
function to setup a modified version of the
:py:data:`~pytest_ngsfixtures.plugin.flat` fixture that copies the
test files (`test_workflow_flat_copy.py`):

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_flat_copy.py
   :language: python



Setting up a docker container fixture
+++++++++++++++++++++++++++++++++++++

The previous section would have been unnecessary if only local tests
were run, but copying test files is necessary for container-based
tests. In the following test script (`test_workflow_docker.py`), we
add a lot of new functionality.

First, we import the :py:mod:`docker` module to interact with docker,
along with :py:mod:`os` and :py:mod:`pytest`:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 2-4

Then, we add a `container` fixture that sets up a container based on
the snakemake docker image
`quay.io/biocontainers/snakemake:4.5.0--py36_0
<https://quay.io/repository/biocontainers/snakemake?tag=latest&tab=tags>`_:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 13-40

Finally, we add the `container` fixture to the test function call:

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_docker.py
   :language: python
   :lines: 47-54


Parametrized tests on running environment
++++++++++++++++++++++++++++++++++++++++++

We have now written tests for local execution and execution in a
container. By parametrizing the tests, we can combine the two cases in
one test function. To do this we modify the test function as follows
(see `test_workflow_parametrize.py`):

.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_parametrize.py
   :language: python
   :lines: 49-58

The parametrization is done indirectly via the `container` fixture. We
modify this fixture to return `None` if the request parameter equals
`local`, and if the parameter equals `docker` we return the container:


.. literalinclude:: ../pytest_ngsfixtures/tests/test_workflow_parametrize.py
   :language: python
   :lines: 16-42

Now, running

.. code-block:: shell

   pytest -v -s tests/test_workflow_parametrize.py

will execute two tests, one for the local environment, one in the
docker container.
