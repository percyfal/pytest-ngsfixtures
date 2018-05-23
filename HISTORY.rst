History
=======

0.7.1 (2018-05-23)
------------------

Bugfixes
++++++++

* Update busybox images for tests (#59)
* Fix failing test (#58)


0.7.0 (2018-05-23)
------------------

Breaking changes
+++++++++++++++++

This is a major update in which the API has changed considerably.
Notably, most of the code for generating fixtures has been removed and
refactored completely. Most importantly, the factory functions have
been replaced by a small number of fixtures that can be configured via
the `pytest.mark` helper.

In addition, most data files have been removed
in an attempt to make the package as small as possible. As the
location of test data has been decoupled from package functionality,
it makes more sense to distribute package data separately.

See the API documentation for more information.


Features
++++++++

* Remove application data (#30)
* Simplify config.runfmt_alias function (#56)
* Only package tiny sequence data (#55)
* Simplify sample layout configuration (#57)

0.6.4 (2018-01-31)
------------------

* Add docker-py as a dependency (#52)


0.6.3 (2018-01-02)
------------------

* Remove obsolete working directory argument - requires snakemake >=
  4.4.0
* Install correct docker API (#50)
* Allow modifying path in shell wrapper (#51)

0.6.2 (2017-12-19)
------------------

Add shell wrappers and wrappers for easily setting up workflow tests.

Add tutorial.

Bugfixes.

* Update pypi badge
* Remove tox.ini
* Defer setting alias to FixtureFile (#42)
* ReadFixtureFile.SM now returns id (#39)
* Options ngs_layout and ngs_runfmt are now lists (#41)
* Update project layout configuration (#40)
* Add function to return runfmt and alias as tuple (#43)
* Read 1 and 2 have same id when alias required (#45)
* Census is not increased for read 2 (#44)
* Add option to only setup sampleinfo (#47)
* Add tutorial (#46)
* Add working snakemake tests (#8)

0.6.1 (2017-11-22)
------------------

Added some fixes that turned out to be necessary for optional performance.

* Add fixture that parametrizes over input parameters (#37)
* Fix bug that returned wrong number of snakemake targets in application output generation (#36)
* Add travis builds (#35)
* Fix reference layout error for python 3.5 (#34)
* Update option defaults (#32)
* Expose fewer predefined fixtures via plugin (#31)
* Unify parameter names (#33)


0.6.0 (2017-11-21)
------------------

This is a major revision of the code. Several new abstraction classes
have been introduced to ease interaction with local test files, along
with new factory functions. For backwards compatibility, most factory
functions should work as previously. Documentation has been much
improved.

* Clarify fixture function naming convention (#29)
* Expose bulk of factory inner functions (#24)
* Create separate module for os-related functions (#27)
* Use separate conda build statements to build for different python versions (#23)

0.5.2 (2017-11-16)
------------------

* Add pool fixtures (#22)
* Add safe_copy function (#21)

0.5.1 (2017-10-25)
------------------

* Change name to pytest-ngsfixtures (#20)
* Add bcftools versions 1.4, 1.4.1, 1.5, 1.6
* Add bowtie 1.2.1.1

0.5.0 (2017-09-25)
------------------

* Add star application
* Add vsearch application
* Add rseqc application
* Add snakemake dependency
* Update docs

* Separate qualimap pe and se output (#12)
* Add mapdamage2 (#11)
* Fix mapdamage2 missing output (#18)
* Use realpath to determine download url (#17)
* Rename download_ngsfixtures_data.py to pytest_ngsfixtures_download_data.py
* Update versions for samtools

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
