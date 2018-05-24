# -*- coding: utf-8 -*-
"""Plugin configuration module for pytest-ngsfixtures"""
import os
import re
import pytest
from pytest_ngsfixtures.config import layout, reflayout
from pytest_ngsfixtures.os import safe_mktemp, safe_copy, safe_symlink

_help_ngs_threads = "set the number of threads to use in test"


def pytest_addoption(parser):
    group = parser.getgroup("ngsfixtures", "next-generation sequencing fixture options")
    group.addoption(
        '--nt',
        '--ngs-threads',
        action="store",
        dest="ngs_threads",
        default=1,
        help=_help_ngs_threads,
    )


def pytest_configure(config):
    pass


def _update_options(request, fixturename, options, exclude=["request", "tmpdir_factory"]):
    d = {}
    keys = set(request.fixturenames).difference(exclude)
    for k in keys:
        try:
            d[k] = request.getfixturevalue(k)
        except:
            pass
    options.update(d)
    if fixturename in request.keywords:
        options.update(request.keywords.get(fixturename).kwargs)


@pytest.fixture
def testdata(request, tmpdir_factory):
    """Return a temporary directory path object pointing to the root
    directory where generic test data are located.

    Examples:

       .. code-block:: python

          @pytest.mark.testdata(data={'foo.txt': 'bar.txt'})
          def test_data(testdata):
              print(testdata.listdir())

    """
    options = {
        'data': {},
        'numbered': False,
        'dirname': '',
        'testdir': '',
    }
    _update_options(request, 'testdata', options)
    options['dirname'] = os.path.join(options['testdir'], options['dirname'])
    assert isinstance(options['data'], dict), "'data' option must be a dictionary of dst:src value pairs"
    p = safe_mktemp(tmpdir_factory, **options)
    f = safe_copy if options['copy'] else safe_symlink
    for dst, src in options['data'].items():
        f(p, src, dst)
    return safe_mktemp(tmpdir_factory, **options)


@pytest.fixture
def samples(request, tmpdir_factory):
    """Return a temporary directory path object pointing to the root
    directory where samples are located.

    The samples directory path name can be changed with
    @pytest.mark.samples. In addition, the data layout can be
    parametrized with @pytest.mark.parametrize.

    Examples:

       .. code-block:: python

          @pytest.mark.parametrize("layout", [{'s1.fastq.gz': '/path/to/foo.fastq.gz'},
                                              {'s2.fastq.gz': '/path/to/foo.fastq.gz'}])
          @pytest.mark.samples(dirname="foo")
          def test_samples(samples, layout):
              print(samples.listdir())

    """
    options = {
        'numbered': False,
        'dirname': 'data',
        'testdir': '',
        'layout': layout['flat'],
        'copy': True,
    }
    _update_options(request, 'samples', options)
    options['dirname'] = os.path.join(options['testdir'], options['dirname'])
    p = safe_mktemp(tmpdir_factory, **options)
    assert isinstance(options['layout'], dict), "samples 'layout' option must be a dictionary of dst:src value pairs"
    p = safe_mktemp(tmpdir_factory, **options)
    f = safe_copy if options['copy'] else safe_symlink
    for dst, src in options['layout'].items():
        f(p, src, dst)
    return p


@pytest.fixture
def ref(request, tmpdir_factory):
    """Return a temporary directory path object pointing to the location
    of reference files.

    The reference directory path name can be changed with
    @pytest.mark.ref(dirname="refdirname")

    Examples:

       .. code-block:: python

          @pytest.mark.ref(dirname="foo", data={'ref.fa': '/path/to/ref.fa'})
          def test_ref(ref):
              print(ref)
    """
    options = {
        'testdir': '',
        'dirname': 'ref',
        'data': reflayout,
        'copy': True,
    }
    _update_options(request, 'ref', options)
    options['dirname'] = os.path.join(options['testdir'], options['dirname'])
    p = safe_mktemp(tmpdir_factory, **options)
    f = safe_copy if options['copy'] else safe_symlink
    for dst, src in options['data'].items():
        f(p, src, dst, ignore_errors=True)
    return p
