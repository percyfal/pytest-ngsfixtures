Usage
=====

This section gives examples of general usage. For a tutorial on
setting up workflow tests, jump to the :ref:`tutorial` section. The
:ref:`modindex` contains more code examples related to each module and
function.

Next-generation sequencing fixtures
-----------------------------------

One of the main purposes of :py:mod:`pytest_ngsfixtures` is to provide
predefined test fixtures that can be used to test applications, such
as workflows. The predefined test fixtures consist of a test path
(formally a :py:class:`py._path.local.LocalPath` object) in which test
files have been setup following some file organization setup,
henceforth referred to as *test layout* or simply *layout*. Basically,
a layout is a set of links to (or copies of) the distributed data
files, where the link organization and naming reflect typical file
naming schemes of sequencing files delivered by sequence providers or
as used in projects. Currently there are predefined test fixtures for
sequence data and reference data, with the main purpose of being used
for testing analysis workflows from scratch.

The plugin contains two :ref:`fixture-factories` that generate sample
layouts (:py:func:`~pytest_ngsfixtures.factories.sample_layout`) and
reference data
(:py:func:`~pytest_ngsfixtures.factories.reference_layout`). There are
two predefined reference layouts and nine predefined sample layouts.
The reference layouts (:py:data:`~pytest_ngsfixtures.plugin.ref` and
:py:data:`~pytest_ngsfixtures.plugin.scaffolds`) and one sample layout
(:py:data:`~pytest_ngsfixtures.plugin.flat`) are defined at the plugin
level and always loaded. The remaining eight sample layouts are defined in the
:py:mod:`~pytest_ngsfixtures.fixtures` module:

:py:data:`~pytest_ngsfixtures.fixture.sample`,
:py:data:`~pytest_ngsfixtures.fixture.sample_run`,
:py:data:`~pytest_ngsfixtures.fixture.sample_project_run`,
:py:data:`~pytest_ngsfixtures.fixture.pop_sample`,
:py:data:`~pytest_ngsfixtures.fixture.pop_sample_run`,
:py:data:`~pytest_ngsfixtures.fixture.pop_sample_project_run`,
:py:data:`~pytest_ngsfixtures.fixture.pool_pop_sample`,
:py:data:`~pytest_ngsfixtures.fixture.pool_pop_sample_run`

To use a fixture, simply depend on it in a test, e.g.:

.. code-block:: python

   # flat fixture is always loaded
   def test_foo(flat):
       # Do something with flat

   # sample is not automatically loaded
   from pytest_ngsfixtures.fixtures import sample

   # ref fixture is always loaded
   def test_bar(sample, ref):
       # Do something with sample and ref


Parametrized fixtures
+++++++++++++++++++++

There are also two parametrized fixtures,
:py:func:`~pytest_ngsfixtures.fixture.psample` and
:py:func:`~pytest_ngsfixtures.fixture.pref` that generate fixtures
depending on values of plugin options (primarily
:ref:`plugin-option-runfmt`, :ref:`plugin-option-layout`, and
:ref:`plugin-option-ref`). For instance, the following command would
generate all combinations of provided layouts and run formats:

.. code-block:: shell

   pytest --ngs-runfmt sample sample_run --ngs-layout individual pool

provided of course there is a test that requires the
:py:func:`~pytest_ngsfixtures.fixtures.psample` fixture.

.. _fixture-factories:

Fixture factories
------------------

Layout fixture factories
+++++++++++++++++++++++++

The predefined sample layouts cover some common cases. However,
alternative layouts can be added by using the
:py:func:`~pytest_ngsfixtures.factories.sample_layout` factory
function:

.. code-block:: python

   from pytest_ngsfixtures import factories

   custom_samples = factories.sample_layout(
       dirname="foo",
       sample=["CHS.HG00512", "YRI.NA19238"],
       platform_unit=['bar', 'foobar'],
       paired_end=[True, False],
       short_name=False,
       runfmt="{SM}/{SM}_{PU}",
       numbered=False,
       scope="function",
   )

   def test_custom(custom_samples):
       # do something with custom_samples

The plugin option :ref:`plugin-option-fixture` (see
:ref:`plugin-options` below) shows the fixture layout. For instance,
using this option with the sample layout would generate the following
information upon running a test that depends on the sample fixture:

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

Note that the
:py:func:`~pytest_ngsfixtures.factories.reference_layout` only
provides a choice between two reference data fixtures. The `ref`
treats the reference as one chromosome, whereas the `scaffolds`
fixture partitions the reference into several scaffolds.

File fixture factories
+++++++++++++++++++++++

In addition to sequence and reference input data, there is a
collection of downstream files, such as bam files, and application
output files, e.g. from samtools and fastqc. As of version 0.6.0,
there are three fixture factory functions,
:py:func:`~pytest_ngsfixtures.factories.filetype`,
:py:func:`~pytest_ngsfixtures.factories.fileset` and
:py:func:`~pytest_ngsfixtures.factories.application_output`. All
factory functions take as input a path, which is either a target file
name or a directory, and returns a
:py:class:`~pytest_ngsfixtures.file.FixtureFile` path with setup
fixture files. For consistency with :py:mod:`py.path`,
:py:class:`~pytest_ngsfixtures.file.FixtureFile` subclasses
:py:mod:`py._path.local.LocalPath`. See
:py:mod:`pytest_ngsfixtures.file` for more
:py:class:`~pytest_ngsfixtures.file.FixtureFile` subclasses.

The filetype factory generates a fixture for a single file, whereas
the fileset factory generates a fixture for several files. The
application output factory is a wrapper for application output data,
returning a
:py:class:`~pytest_ngsfixtures.file.ApplicationOutputFixture`.

.. code-block:: python

   from pytest_ngsfixtures import factories

   bam = factories.filetype("PUR.HG00731.tiny.bam", scope="function")

   def test_bam(bam):
       # Do something with bam file


   bamset = factories.fileset(src=["PUR.HG00731.tiny.bam",
				   "PUR.HG00733.tiny.bam"],
				   fdir="bamset", scope="function")

   def test_bamset(bamset):
       # Do something with bamset

   samtools_flagstat = factories.application_output("samtools", "samtools_flagstat", "1.2")

   def test_parse_samtools_flagstat(samtools_flagstat):
       # Do something with samtools_flagstat output


If you provide the path as a relative path it will be interpreted as
relative to ``pytest_ngsfixtures/data`` in the ``pytest-ngsfixtures``
installation directory. However, a full path is treated as such,
meaning you can use the file fixture factories to setup fixtures for
any file or fileset on the filesystem. Note that this does not apply
to the :py:func:`~pytest_ngsfixtures.factories.application_output`
fixture factory.

.. code-block:: python

   from pytest_ngsfixtures import factories

   bam = factories.filetype("/path/to/mybam.bam", scope="function")

   def test_bam(bam):
       # Do something with bam file


   bamset = factories.fileset(src=["/path/to/bam1.bam",
				   "/path/to/bam2.bam"],
				   fdir="bamset", scope="function")

   def test_bamset(bamset):
       # Do something with bamset


Fixture setup wrappers
----------------------

The factory functions described in the previous section wrap and
return an inner function decorated with the :py:func:`pytest.fixture`
decorator. The inner function in turn calls setup wrappers that can be
accessed directly if one wishes to setup fixtures explicitly.

Layout setup wrappers
+++++++++++++++++++++

For instance, :py:func:`~pytest_ngsfixtures.layout.sample_layout`
calls the function
:py:func:`~pytest_ngsfixtures.layout.setup_sample_layout` that sets up
the fixture files. The function could be called explicitly to setup a
fixture:

.. code-block:: python

   import pytest
   from pytest_ngsfixtures import layout

   @pytest.fixture
   def short_layout():
       p = setup_sample_layout(tmpdir, layout="short", runfmt="{SM}_{PU}")
       return p

   def test_layout(short_layout):
       # Do something with short_layout


In addition, there is a function
:py:func:`~pytest_ngsfixtures.layout.setup_reference_layout` that sets
up reference fixture files.

File setup wrappers and fixture file classes
+++++++++++++++++++++++++++++++++++++++++++++

The file setup wrappers
:py:func:`~pytest_ngsfixtures.file.setup_filetype` and
:py:func:`~pytest_ngsfixtures.file.setup_fileset` setup single files
and file sets, respectively.

There are also a number of classes that abstract the test files and
their sources. The base class
:py:class:`~pytest_ngsfixtures.file.FixtureFile` subclasses
:py:class:`py._path.local.LocalPath` and abstracts the test output
file. It adds a number of attributes, most importantly
:py:attr:`pytest_ngsfixtures.file.FixtureFile.src` that stores a
:py:class:`py._path.local.LocalPath` version of the data source. Test
files can be symlinked (default) or copied:

.. code-block:: python

   from pytest_ngsfixtures.file import FixtureFile

   @pytest.fixture
   def foo_link():
       f = FixtureFile("foo.txt", src="/path/to/foo.txt")
       # Setup the file fixture
       f.setup()
       return f

   @pytest.fixture
   def foo_copy():
       f = FixtureFile("foo.txt", src="/path/to/foo.txt", copy=True)
       # Setup the file fixture
       f.setup()
       return f

   def test_foo(foo_link, foo_copy):
       assert foo_link.realpath() == foo_copy.realpath()


The classes that subclass
:py:class:`~pytest_ngsfixtures.file.FixtureFile` are
:py:class:`~pytest_ngsfixtures.file.FixtureFileSet`
:py:class:`~pytest_ngsfixtures.file.ReadFixtureFile`
:py:class:`~pytest_ngsfixtures.file.ReferenceFixtureFile`
:py:class:`~pytest_ngsfixtures.file.ApplicationFixtureFile` and
:py:class:`~pytest_ngsfixtures.file.ApplicationOutputFixture`. There
is a fixture wrapper
:py:func:`~pytest_ngsfixtures.file.fixturefile_factory` that can be
used to try creating one of these classes based on the parameters and
the existence of the (inferred) source file:

.. code-block:: python

   >>> import py
   >>> from pytest_ngsfixtures.file import fixturefile_factory
   >>> p = py.path.local()
   >>> p = fixturefile_factory(p.join("ref.fa"))
   >>> type(p)
   <class 'pytest_ngsfixtures.file.ReferenceFixtureFile'>


Files
-----

Fixture files live in subdirectories of the
:py:data:`pytest_ngsfixtures/data` directory:

applications/{application}

   Application output files. Subfolders represent applications in
   which output data for several subcommands, versions, and sequencing
   modes are stored. The application output can easily be setup as
   test fixtures with the
   :py:class:`~pytest_ngsfixtures.file.ApplicationOutputFixture` class.

applications/{pe,se}

   The subdirectories
   :py:data:`pytest_ngsfixtures/data/applications/pe` and
   :py:data:`pytest_ngsfixtures/data/applications/se` currently
   contain bam files for setting up tests with bam file fixtures. The
   output files can be setup as test fixtures with the
   :py:class:`~pytest_ngsfixtures.file.ApplicationFixtureFile` class.

ref/

   Reference data files which can be setup as test fixtures with the
   :py:class:`~pytest_ngsfixtures.file.ReferenceFixtureFile` class.


medium/

  Medium-sized sequence files.

small/

  Small sequence files.

tiny/

  Tiny sequence files.

yuge/

  Yuge sequence files. All sequence files can be setup as test fixtures with the
  :py:class:`~pytest_ngsfixtures.file.ReadFixtureFile` class.


Each sequence directory contains the same samples in different sizes:

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
---------------

Custom sample layouts
++++++++++++++++++++++

In addition to the predefined sample layouts, it is possible to define
custom layouts by use of the
:py:func:`~pytest_ngsfixtures.factories.sample_layout` factory
function. Basically, the fixture creates links to the data files. The
fixture link names are determined by the parameter ``runfmt``, which
is a `python mini-format string
<https://docs.python.org/3/library/string.html#formatspec>`_. The
format arguments relate to the function parameters as follows:

SM

  sample - list of sample names (one or several of CHS.HG00512,
  CHS.HG00513, PUR.HG00731, PUR.HG00733, YRI.NA19238, and
  YRI.NA19239.)

PU

  platform_unit - platform unit names, e.g. flowcell name.

BATCH

  batches - batch (project) name, e.g. if a sequencing center run
  several rounds of sequencing of a sample

POP

  populations - population names

:py:func:`~pytest_ngsfixtures.factories.sample_layout` generates
output file names by iterating over the parameters and formatting
names according to runfmt. For instance, if
``runfmt="{SM}/{SM}_{PU}"``, values in ``sample`` and
``platform_unit`` will be used to produce the final file names. In
this case, ``sample`` and ``platform_unit`` must be of equal length.

See the predefined fixtures in :py:mod:`pytest_ngsfixtures.plugin` and
the tests for examples.

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
layout fixtures by use of the ``request.getfuncargvalue`` function. In
addition, the parametrization is done over the plugin option
:ref:`plugin-option-layout`, which enables selecting from the command line what
layouts to use (see next section).

.. _plugin-options:

Plugin options
--------------

The plugin defines three options that can be used to select and show
predefined fixtures.

-X, --ngs-size
++++++++++++++

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

.. _plugin-option-layout:

-L, --ngs-layout
+++++++++++++++++

Select one or more of the predefined sample layouts for parametrized
fixtures. See documentation for
:py:func:`pytest_ngsfixtures.fixtures.psample` for
:py:func:`pytest_ngsfixtures.fixtures.pref`. Example usage:

.. code-block:: shell

   pytest -L individual

Here, the :py:func:`~pytest_ngsfixtures.fixtures.psample` fixture will
return fixtures with the `individual` sample layout.

.. _plugin-option-runfmt:

--ngs-runfmt
+++++++++++++++++

Layout sequence files according to one or more formats determined by
python miniformat strings. The format specifiers should be one of `SM`
(sample), `PU` (platform unit), `POP` (population), `BATCH` (batch
name). For instance, the following example would setup samples in the
root test directory using sample and platform unit as unique
identifier prefix:

.. code-block:: shell

   pytest --ngs-runfmt "{SM}/{SM}_{PU}"

There are also predefined aliases that can be used for convenience;
see :py:data:`pytest_ngsfixtures.config.sample_conf`. For instance,
the following is equivalent to the option above:

.. code-block:: shell

   pytest --ngs-runfmt sample


.. _plugin-option-pool:

--ngs-pool
+++++++++++++++++

Run tests on pooled data.

.. _plugin-option-copy:

--ngs-copy
+++++++++++++++++

Copy tests instead of symlinking. Only affects parametrized fixtures.

.. _plugin-option-ref:

--ngs-ref
+++++++++++++++++

Use ref reference layout instead of scaffolds. Only affects
parametrized fixtures.



.. _plugin-option-fixture:

-F, --ngs-show-fixture
+++++++++++++++++++++++

Print information on the files that are setup in the fixture.
