pytest-ngsfixtures
==================

.. image:: https://anaconda.org/percyfal/pytest-ngsfixtures/badges/version.svg
	   :target: https://anaconda.org/percyfal/pytest-ngsfixtures
.. image:: https://badge.fury.io/py/pytest-ngsfixtures.svg
	   :target: https://badge.fury.io/py/pytest-ngsfixtures
.. image:: https://travis-ci.org/percyfal/pytest-ngsfixtures.svg?branch=master
	   :target: https://travis-ci.org/percyfal/pytest-ngsfixtures


About
=====

This is a `pytest plugin
<http://doc.pytest.org/en/latest/plugins.html>`_ that provides
functionality for next generation sequencing `pytest fixtures
<http://doc.pytest.org/en/latest/fixture.html>`. There are some
predefined fixtures, but the main functionality depends on configuring
fixtures via the `pytest.mark` helper function.

See the `pytest-ngsfixtures documentation`_ for more information and
usage.

* Free software: GNU General Public License v3

Features
--------

- a small test ngs data set
- predefined sample layouts
- wrappers for quickly setting up workflow tests


Installation
============

.. code-block:: bash

   $ conda install -c percyfal pytest-ngsfixtures
   $ pip install pytest-ngsfixtures


Usage
=========

You can easily setup a test requiring the predefined `samples` and
`ref` fixtures:

.. code-block:: python
   
   def test_data(samples, ref):
    shell("bwa index {}".format(ref.join("scaffolds.fa")))
    shell("bwa mem {} {} {} | samtools view -b > {}".format(
        ref.join("scaffolds.fa"),
        samples.join("s1_1.fastq.gz"),
        samples.join("s1_2.fastq.gz"),
        samples.join("s1.bam")
    ))
    assert samples.join("s1.bam").exists()

The samples and ref fixtures can also be configured to use local
files:

.. code-block:: python

   import pytest
		
   @pytest.mark.samples(layout={'s1_1.fastq.gz': "/path/to/read1.fastq.gz",
		                's1_2.fastq.gz': "/path/to/read2.fastq.gz"})
   @pytest.mark.ref(data={'ref.fa': "/path/to/reference.fa"})
   def test_data(samples, ref):
       # Do something with data

In addition, there are wrapper functions and fixtures for workflow
managers, including Snakemake.

.. code-block:: python

   import pytest
   from pytest_ngsfixtures.wm.snakemake import snakefile, run as snakemake_run

   # By default, the snakefile fixture assumes there is a Snakefile in
   # the test file directory
   def test_workflow(samples, snakefile):
       snakemake_run(snakefile, options=["-d", str(samples)])
       assert samples.join("results.txt").exists()


See the `pytest-ngsfixtures documentation`_ for more examples.
      
       

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`pytest-ngsfixtures documentation`: https://percyfal.github.io/pytest-ngsfixtures/
