pytest-ngsfixtures
==================

.. image:: https://anaconda.org/percyfal/pytest-ngsfixtures/badges/version.svg
	   :target: https://anaconda.org/percyfal/pytest-ngsfixtures
.. image:: https://img.shields.io/pypi/dm/pytest-ngsfixtures.svg
	   :target: https://pypi.python.org/pypi/pytest-ngsfixtures
.. image:: https://badge.fury.io/py/pytest-ngsfixtures.svg
	   :target: https://badge.fury.io/py/pytest-ngsfixtures		    


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

See the `pytest-ngsfixtures documentation`_ for more information and
usage.

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

   $ conda install -c percyfal pytest-ngsfixtures
   $ pip install pytest-ngsfixtures


Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`pytest-ngsfixtures documentation`: https://percyfal.github.io/pytest-ngsfixtures/
