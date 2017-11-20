# -*- coding: utf-8 -*-
import os
import py
from py._path.local import LocalPath
from pytest_ngsfixtures.os import safe_symlink, safe_copy
from pytest_ngsfixtures import ROOT_DIR, DATA_DIR


class FixtureFile(LocalPath):
    def __init__(self, path=None, expanduser=False, **kwargs):
        super(FixtureFile, self).__init__(path, expanduser)
        self._copy = kwargs.get('copy', False)
        self.src = kwargs.get('src', None)
        self._setup_fn = safe_copy if self._copy else safe_symlink

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, src):
        if src is not None:
            assert isinstance(src, LocalPath), "src path must be py._path.local.LocalPath object"
            assert src.realpath().exists(), "src path must exist"
        self._src = src

    @property
    def path(self):
        if self.isdir():
            return self
        else:
            return py.path.local(self.dirname)

    def setup(self):
        self._setup_fn(self.path, self.src, self.basename)

    def __repr__(self):
        return "{} (src: {})".format(self, self.src)


class ReadFixtureFile(FixtureFile):
    _samples = ('CHS', 'CHS.HG00512', 'CHS.HG00513', 'PUR',
                'PUR.HG00731', 'PUR.HG00731.A', 'PUR.HG00731.B',
                'PUR.HG00733', 'PUR.HG00733.A', 'PUR.HG00731.B',
                'YRI', 'YRI.NA19238', 'YRI.NA19239')
    _populations = tuple(['CHS'] * 3 + ['PUR'] * 7 + ['YRI'] * 3)
    _reads = tuple([1, 2])
    _platform_units = tuple([None, '010101_AAABBB11XX', '020202_AAABBB22XX'] + [None] + ['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'] + [None, '010101_AAABBB11XX', '020202_AAABBB22XX'])

    def __init__(self, sample, path=None, expanduser=False,
                 size="tiny", read=1, batch=None,
                 runfmt="{SM}", *args, **kwargs):
        self._size = size
        self.sample = kwargs.get("sample", "CHS.HG00512")
        self._index = self._samples.index(sample)
        self._population = kwargs.get("population", self._populations[self._index])
        self._platform_unit = kwargs.get("platform_unit", self._platform_units[self._index])
        self._batch = batch
        self._runfmt = runfmt
        self.read = read
        src = py.path.local(os.path.join(DATA_DIR, self.size, "{}{}".format(sample, self.fastq_suffix)))
        if path is None:
            path = str(self)
        else:
            if isinstance(path, str):
                path = py.path.local(path)
            elif isinstance(path, LocalPath):
                if path.isdir():
                    path = path.join(src.basename)
            else:
                pass
        super(ReadFixtureFile, self).__init__(src=src, path=path, expanduser=expanduser, **kwargs)

    @property
    def sample(self):
        return self._sample

    @sample.setter
    def sample(self, sample):
        assert sample in self._samples, "sample has to be one of {}".format(", ".join(self._samples))
        self._sample = sample

    @property
    def read(self):
        return self._read

    @read.setter
    def read(self, read):
        assert read in self._reads, "read has to be one of {}".format(", ".join(self._reads))
        self._read = read

    @property
    def size(self):
        return self._size

    @property
    def population(self):
        return self._population

    @property
    def platform_unit(self):
        return self._platform_unit

    @property
    def batch(self):
        return self._batch

    @property
    def runfmt(self):
        return self._runfmt

    @property
    def fastq_suffix(self):
        return "_{}.fastq.gz".format(self.read)

    def __iter__(self):
        yield 'POP', self.population
        yield 'PU', self.platform_unit
        yield 'SM', self.sample
        yield 'BATCH', self.batch

    def __str__(self):
        return self.runfmt.format(**dict(self)) + self.fastq_suffix


class ReferenceFixtureFile(FixtureFile):
    def __init__(self, src, *args, **kwargs):
        if isinstance(src, str):
            src = py.path.local(os.path.join(DATA_DIR, "ref", src))
        super(ReferenceFixtureFile, self).__init__(src, *args, **kwargs)


class ApplicationFixtureFile(FixtureFile):
    _end = set(["se", "pe"])

    def __init__(self, application, command, version, end="se", *args, **kwargs):
        src = py.path.local(os.path.join(DATA_DIR, "applications", application, version, end))
        super(ApplicationFixtureFile, self).__init__(src, *args, **kwargs)
