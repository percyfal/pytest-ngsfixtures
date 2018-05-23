Usage
=====

This section gives examples of general usage. For a tutorial on
setting up workflow tests, jump to the :ref:`tutorial` section. The
:ref:`modindex` contains more code examples related to each module and
function.

Next-generation sequencing fixtures
-----------------------------------

One of the main purposes of :py:mod:`pytest_ngsfixtures` is to provide
functionality for setting up fixtures that can be used to test
applications, such as workflows. The predefined test fixtures consist
of a test path (formally a :py:class:`py._path.local.LocalPath`
object) in which test files have been setup following some file
organization setup, henceforth referred to as *test layout* or simply
*layout*. Basically, a layout is a set of links to (or copies of) the
test data files. Currently there are predefined test fixtures for
sequence data and reference data, with the main purpose of being used
for testing analysis workflows from scratch.


Fixtures
--------

There are three main fixtures that can be configured with the
`pytest.mark` helper. In general, the test data files are defined as a
dictionary of key:value pairs that are passed via the `data` option
(or similar option) to the `pytest.mark.testdata` helper. Some
fixtures predefine output directories which can be configured with the
`dirname` option. The key corresponds the test fixture file path
*relative to the pytest root directory*, whereas the value is the path
to the test data file.

:py:func:`pytest_ngsfixtures.plugin.testdata`
+++++++++++++++++++++++++++++++++++++++++++++

A generic fixture for setting up test data.


:py:func:`pytest_ngsfixtures.plugin.samples`
+++++++++++++++++++++++++++++++++++++++++++++

A fixture for setting up sequence read data. Data files are defined
via the `layout` option and are placed in the `data` directory. The
`layout` and `dirname` options can also be configured via
`pytest.mark.parametrize`, which enables the parametrization over
different sample layouts:

.. code-block:: python

   @pytest.mark.parametrize("layout", [{'s1.fastq.gz': '/path/to/foo.fastq.gz'}, 
		                       {'s2.fastq.gz': '/path/to/foo.fastq.gz'}])
   def test_samples(samples, layout):
       print(samples.listdir())

There are a number of predefined layouts defined in
the :py:data:`pytest_ngsfixtures.config.layout` dictionary.
       

:py:func:`pytest_ngsfixtures.plugin.ref`
+++++++++++++++++++++++++++++++++++++++++++++

A fixture for setting up reference data, by default in the `data`
directory.



Files
-----

Fixture files live in subdirectories of the
:py:data:`pytest_ngsfixtures/data` directory:

ref/

   Reference data files which are used by default by the
   :py:data:`~pytest_ngsfixtures.plugin.ref` fixture.

seq/

  Sequence files.

The sequence directory consists of the following files:

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
generate differing variant call sets. The pools are simply
concatenated versions of the individual files, with a ploidy of 4.


Advanced usage
---------------


Parametrizing existing sample layouts
++++++++++++++++++++++++++++++++++++++

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
layout fixtures by use of the ``request.getfuncargvalue`` function.

.. _plugin-options:

Plugin options
--------------

-nt, --ngs-threads
++++++++++++++++++

Set the number of threads to use in a given test.
