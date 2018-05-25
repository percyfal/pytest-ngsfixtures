# -*- coding: utf-8 -*-
"""Plugin configuration module for pytest-ngsfixtures"""
import os
import re
import pytest
from py._path.local import LocalPath
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


class Fixture(LocalPath):
    """Fixture class to setup fixture represented as a
    :py:class:`~py._path.local.LocalPath` object pointing to the root
    test directory where data are located.

    Args:
      name (str): fixture name (one of testdata, samples, ref)
      request (_pytest.fixtures.SubRequest): pytest request object
      datakey (str): data key label
      path (str): test directory path; overrides call to tmpdir_factory

    Keyword Args:
      copy (bool): copy or link data
      data (dict): key value mapping of destination and source files
      dirname (str): fixture directory; prefixed by testunit if provided
      ignore_errors (bool): ignore errors should target file exist
      numbered (bool): create numbered test directories
      testunit (str): group tests in directory named testunit relative to tmpdir_factory basename
    """
    def __init__(self, name='testdata', request=None, datakey='data', path=None, **kwargs):
        self._name = name
        self._request = request
        self._datakey = datakey
        self._path = path
        self._d = {
            'copy': True,
            'data': {},
            'dirname': '',
            'ignore_errors': False,
            'numbered': False,
            'testunit': '',
        }
        self._d[datakey] = {}
        self._d.update(**kwargs)
        if self._request is not None:
            self._update_options()
        if self._datakey != 'data':
            self._d['data'] = self._d[self._datakey]
        assert isinstance(self._d['data'], dict), "'data' option must be a dictionary of dst:src value pairs"
        self._setup_fixture_data()

    def keys(self):
        return self._d.keys()

    def __getitem__(self, item):
        return self._d[item]

    def __iter__(self):
        return iter(self._d)

    def _update_options(self):
        for k in self.keys():
            try:
                self._d[k] = self._request.getfixturevalue(k)
            except:
                pass
        if self._name in self._request.keywords:
            self._d.update(self._request.keywords.get(self._name).kwargs)

    def _setup_fixture_data(self):
        self._d['dirname'] = os.path.join(str(self._d['testunit']), self._d['dirname'])
        if self._request is not None:
            tmpdir_factory = self._request.getfixturevalue("tmpdir_factory")
        else:
            from _pytest.tmpdir import TempdirFactory
            tmpdir_factory = TempdirFactory(pytest.config)
        if self._path is not None:
            p = self._path
        else:
            p = safe_mktemp(tmpdir_factory, **dict(self))
        self.strpath = str(p)
        f = safe_copy if self._d['copy'] else safe_symlink
        for dst, src in self._d['data'].items():
            f(p, src, dst, ignore_errors=self._d['ignore_errors'])


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
    return Fixture('testdata', request)


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
    return Fixture('samples', request, datakey="layout", layout=layout['flat'])


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
    return Fixture('ref', request, datakey="reflayout", ignore_errors=True, reflayout=reflayout)
