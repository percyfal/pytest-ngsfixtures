Tutorials
=========

In this section we present a couple of applied use cases in the form
of tutorials.

Setting up a snakemake workflow with a predefined sample layout
---------------------------------------------------------------

In order to use the test fixtures with the `snakemake workflow manager
<http://snakemake.readthedocs.io/en/stable/>`_, we need to setup 1. a
Snakefile and 2. a test file.

The Snakefile defines rules that declare what to do with the input
data. In a real-life scenario, we would run various bioinformatics
applications to transform the input into some meaningful output. Here,
we perform operations using basic shell commands, but the same
principle applies to a bioinformatics workflow.

The test file defines a test that depends on one or several of the
pytest_ngsfixtures fixtures.


Setting up a snakemake workflow



Setting up a snakemake workflow with a custom sample layout
-----------------------------------------------------------

TODO

Advanced: parametrize tests on runfmt specification
---------------------------------------------------

TODO
