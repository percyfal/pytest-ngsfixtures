=======
History
=======

0.4.0 (2017-03-28)
------------------

* Add picard output data
* Add functions for dealing with application fixtures
* Move docs to gh-pages
* Add pytest_ngsfixtures_add_application.py for templating new
  applications
* Application outputs now implemented as dictionaries for
  multiple-output applications


0.3.1 (2017-03-03)
------------------

Defer download to script, minor bug fixes

* Add application_fixtures to config module
* Fix sample_alias bug (#4)
* Add script download_ngsfixtures_data.py for manual download of data (#5)


0.3.0 (2017-03-02)
------------------

Add application data, pool data, and functions for downloading data

* Add application data for cutadapt, fastqc, qualimap and samtools
* Add pooled sequencing data
* Add functionality for downloading large data sets
* Improve make targets for easier releases
* Minor bug fixes


0.2.0 (2017-02-24)
------------------

Add new reference files, test files, and factory functions.

* Use snakemake instead of make to generate data files
* Add separate test file for factory functions
* Add scaffold file with randomly inserted N's
* Improve safe_symlink
* Add threads options for running tests
* Add Snakefile and rules for generating application files
* Add fileset, filetype factory functions


0.1.0 (2017-01-24)
------------------

* First release on PyPI.
