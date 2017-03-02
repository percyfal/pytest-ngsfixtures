====================
 pytest-ngsfixtures
====================

.. image:: https://anaconda.org/percyfal/pytest-ngsfixtures/badges/version.svg
	   :target: https://anaconda.org/percyfal/pytest-ngsfixtures

About
=====

This is a `pytest plugin
<http://doc.pytest.org/en/latest/plugins.html>`_ that enables next
generation sequencing `pytest fixtures
<http://doc.pytest.org/en/latest/fixture.html>`_, including fastq
files and output files from a variety of bioinformatics applications
and tools. There are sequencing fixtures for some common sample
layouts, but it's easy to generate additional sample fixture layouts
using fixture factories.

* Free software: GNU General Public License v3

Features
--------

- ngs data sets of different sizes
- predefined sample layouts
- factories for generating new sample layouts
- result files from a variety of bioinformatics applications and tools


Installation
============

.. code-block:: bash

   $ conda install pytest-ngsfixtures


Usage
=====

Layout fixture factories
------------------------

The plugin contains two fixture factories that generate sample layouts
(**sample_layout**) and reference data (**reference_layout**). A
layout is simply a set of links to the distributed data files, where
the link organization and naming reflect typical file naming schemes
of sequencing files delivered by sequence providers or as used in
projects.

There are seven predefined sample layouts: **flat**, **sample**,
**sample_run**, **sample_project_run**, **pop_sample**,
**pop_sample_run**, and **pop_sample_project_run**, and two reference
layouts: **ref** and **scaffolds**.

To use a fixture, simply depend on it in a test, e.g.:

.. code-block:: python

   def test_foo(sample):
       # Do something with sample

The predefined sample layouts cover some common cases. However,
alternative layouts can be added by using the factory function:

.. code-block:: python

   from pytest_ngsfixtures import factories

   custom_samples = factories.sample_layout(
       dirname="foo",
       samples=["CHS.HG00512", "YRI.NA19238"],
       platform_units=['bar', 'foobar'],
       paired_end=[True, False],
       use_short_sample_names=False,
       runfmt="{SM}/{SM}_{PU}",
   )

   def test_custom(custom_samples):
       # do something with custom_samples

The plugin option **-F** (see **Plugin options** below) shows the
fixture layout. For instance, using this option with the sample layout
would generate the following information upon running a test that
depends on the sample fixture:

.. code-block:: console

   INFO:pytest_ngsfixtures.factories:sample_layout
   INFO:pytest_ngsfixtures.factories:-------------
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s1
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s1/s1_010101_AAABBB11XX_1.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s1/s1_010101_AAABBB11XX_2.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s1/s1_020202_AAABBB22XX_1.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s1/s1_020202_AAABBB22XX_2.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s2
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s2/s2_010101_AAABBB11XX_1.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/s2/s2_010101_AAABBB11XX_2.fastq.gz
   INFO:pytest_ngsfixtures.factories:/tmp/pytest-of-user/pytest-1/sample0/sampleinfo.csv

   
File fixture factories
----------------------

In addition to sequence and reference input data, there is a
collection of downstream files, such as bam files, and application
output files, e.g. from samtools and fastqc. As of version 0.3.0,
there are two fixture factory functions, **filetype** and **fileset**,
that create file fixtures and fileset fixtures, respectively. The
filetype factory generates a fixture for a single file, returning the
path to the file, whereas the fileset factory generates a fixture for
several files, returning the path to the directory in which the files
reside.

.. code-block:: python

   from pytest_ngsfixtures import factories
   
   bam = factories.filetype("applications/pe/PUR.HG00731.tiny.bam", scope="function")

   def test_bam(bam):
       # Do something with bam file

   
   bamset = factories.fileset(src=["applications/pe/PUR.HG00731.tiny.bam",
		                   "applications/pe/PUR.HG00733.tiny.bam"],
                                   fdir="bamset", scope="function")

   def test_bamset(bamset):
       # Do something with bamset


Note that currently you need to provide the path to the file *relative
to* ``pytest_ngsfixtures/data``.
       

Files
=====

Fixture files live in subdirectories of the
``pytest_ngsfixtures/data`` directory:

applications/
  application output files

ref/
  reference data files

medium/
  medium sequence files
  
small/
  small sequence files

tiny/
  tiny sequence files

yuge/
  yuge sequence files

Each sequence directory contain the same samples in different sizes:

::
   
   File name                   Sample ID         Type                Population      
   --------------------------  ------------      -----------------   ------------    
   CHS.HG00512_1.fastq.gz      CHS.HG00512       Individual	     Han-Chinese     
   CHS.HG00513_1.fastq.gz      CHS.HG00513       Individual	     Han-Chinese     
   CHS_1.fastq.gz              CHS               Pool		     Han-Chinese     
   PUR.HG00731.A_1.fastq.gz    PUR.HG00731.A     Individual, run A   Puerto Rico     
   PUR.HG00731.B_1.fastq.gz    PUR.HG00731.B     Individual, run B   Puerto Rico     
   PUR.HG00733.A_1.fastq.gz    PUR.HG00733.A     Individual, run A   Puerto Rico     
   PUR.HG00733.B_1.fastq.gz    PUR.HG00733.B     Individual, run B   Puerto Rico     
   PUR_1.fastq.gz              PUR               Pool, run A	     Puerto Rico     
   YRI.NA19238_1.fastq.gz      YRI.NA19238       Individual	     Yoruban         
   YRI.NA19239_1.fastq.gz      YRI.NA19238       Individual	     Yoruban         
   YRI_1.fastq.gz              YRI               Pool		     Yoruban         


and similarly for read 2. The sequence files have been generated from
the 1000 genomes project, two each from the populations CHS
(Han-Chinese), PUR (Puerto Rico) and YRI (Yoruban). They have been
selected based on mappings to a variable region on chromosome 6 to
ensure that running variant callers on the different data sets will
generate differing variant call sets. When setting up a fixture with
the sample_layout factory function, bear in mind that the parameter
``samples`` **must** be one or several of the labels in the *Sample
ID* column in the table above. The pools are simply concatenated
versions of the individual files, with a ploidy of 4.
		
Advanced usage
==============

Custom sample layouts
---------------------

In addition to the predefined sample layouts, it is possible to define
custom layouts by use of the ``sample_layout`` factory function.
Basically, the fixture creates links to the data files. The fixture
link names are determined by the parameter ``runfmt``, which is a
`python mini-format string
<https://docs.python.org/3/library/string.html#formatspec>`_. The
format arguments relate to the function parameters as follows:

SM
  samples - list of sample names (one or several of CHS.HG00512, CHS.HG00513, PUR.HG00731, PUR.HG00733,
  YRI.NA19238, and YRI.NA19239.)
  
PU
  platform_units - platform unit names, e.g. flowcell name.

BATCH
  batches - batch (project) name, e.g. if a sequencing center run
  several rounds of sequencing of a sample

POP
  populations - population names

``factories.sample_layout`` generates output file names by iterating
over the parameters and formatting names according to runfmt. For
instance, if ``runfmt="{SM}/{SM}_{PU}"``, values in ``samples`` and
``platform_units`` will be used to produce the final file names. In
this case, ``samples`` and ``platform_units`` must be of equal length.

See the predefined fixtures in ``pytest_ngsfixtures.plugin`` and the
tests for examples.
  
Parametrizing existing sample layouts
-------------------------------------

pytest supports parametrizing tests over fixtures. The following code
example shows how to parametrize over the predefined layouts:

.. code-block:: python

   @pytest.fixture(scope="function", autouse=False)
   def data(request):
       return request.getfuncargvalue(request.param)

   @pytest.mark.parametrize("data", pytest.config.getoption("ngs_layout", ["sample"]), indirect=["data"])
   def test_run(data):
       # Do something with data

Here, we define an indirect fixture that calls one of the predefined
layout fixtures by use of the ``request.getfuncargvalue`` function. In
addition, the parametrization is done over the plugin option
``ngs_layout``, which enables selecting from the command line what
layouts to use (see next section).

       
Plugin options
==============

The plugin defines three options that can be used to select and show
predefined fixtures.

-X, --ngs-size
--------------

Select the size of the sequence fixtures (fastq files). There are
currently four sizes to choose from:

1. tiny - 100 sequences (default)
2. small - 1000 sequences
3. medium - 10000 sequences
4. yuge - 1000000000000 sequences!!! No, just kidding, the entire 1000
   genomes bam file is sampled, with a sample maximum at 100000
   sequences

Example:

.. code-block:: shell

   pytest -X small		


-L, --ngs-layout
----------------

Select one of the predefined sample layouts. Note that this option
only affects tests that actually depend on the layouts in some
parametrized way. See ``pytest_ngsfixtures.plugin`` for the setup
of the predefined sample layouts. Example:

.. code-block:: shell

   pytest -L sample sample_data		

-F, --ngs-show-fixture
----------------------

Print information on the files that are setup in the fixture.

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
