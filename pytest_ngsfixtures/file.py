# -*- coding: utf-8 -*-
import os
import re
import py
from py._path.local import LocalPath
from pytest_ngsfixtures.os import safe_symlink, safe_copy
from pytest_ngsfixtures.config import sample_conf
from pytest_ngsfixtures import DATA_DIR


class FixtureFile(LocalPath):
    def __new__(cls, *args, **kwargs):
        obj = super(FixtureFile, cls).__new__(cls)
        cls._data_dir = DATA_DIR
        return obj

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

    @property
    def data_dir(self):
        return self._data_dir

    def __repr__(self):
        return "{} (src: {})".format(self, self.src)


class ReadFixtureFile(FixtureFile):
    census = 0
    _samples = sample_conf.SAMPLES
    _populations = sample_conf.POPULATIONS
    _reads = tuple([1, 2])
    _platform_units = tuple(['010101_AAABBB11XX', '020202_AAABBB22XX', None] +
                            ['010101_AAABBB11XX', '020202_AAABBB22XX', None] +
                            ['010101_AAABBB11XX', '020202_AAABBB22XX'] * 2 +
                            ['010101_AAABBB11XX', '020202_AAABBB22XX', None])

    def __new__(cls, *args, **kwargs):
        obj = super(ReadFixtureFile, cls).__new__(cls)
        cls.census += 1
        return obj

    def __init__(self, sample="CHS.HG00512", path=None,
                 expanduser=False, size="tiny", read=1, batch=None,
                 runfmt="{SM}", alias=None, prefix="s",
                 use_short_sample_name=False, *args, **kwargs):
        self._size = size
        self.sample = sample
        self._index = self._samples.index(sample)
        self._population = kwargs.get("population", self._populations[self._index])
        self._platform_unit = kwargs.get("platform_unit", self._platform_units[self._index])
        self._batch = batch
        self._runfmt = runfmt
        self._short = use_short_sample_name
        self._prefix = "s"
        self.alias = alias
        self.read = read
        src = py.path.local(os.path.join(self.data_dir, self.size, "{}{}".format(self.sample, self.fastq_suffix)))
        if path is None:
            path = self.runfmt.format(**dict(self)) + self.fastq_suffix
        else:
            if isinstance(path, str):
                # Makes custom paths possible
                path = py.path.local(path)
            elif isinstance(path, LocalPath):
                if path.isdir():
                    path = path.join(self.fastq)
            else:
                pass
        super(ReadFixtureFile, self).__init__(src=src, path=path, expanduser=expanduser, **kwargs)

    @property
    def id(self):
        return self.alias if self.alias else self.sample

    @property
    def sample(self):
        return self._sample

    @sample.setter
    def sample(self, sample):
        assert sample in self._samples, "sample has to be one of {}".format(", ".join(self._samples))
        self._sample = sample

    @property
    def SM(self):
        return self._sample

    @property
    def prefix(self):
        return self._prefix

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, alias):
        if self.short:
            self._alias = "{}{}".format(self.prefix, self.census)
        else:
            self._alias = alias

    @property
    def short(self):
        return self._short

    @property
    def read(self):
        return self._read

    @read.setter
    def read(self, read):
        assert read in self._reads, "read has to be one of {}".format(", ".join(self._reads))
        self._read = read

    @property
    def fastq(self):
        return self.runfmt.format(**dict(self)) + self.fastq_suffix

    @property
    def size(self):
        return self._size

    @property
    def population(self):
        return self._population

    @property
    def POP(self):
        return self._population

    @property
    def platform_unit(self):
        return self._platform_unit

    @property
    def PU(self):
        return self._platform_unit

    @property
    def batch(self):
        return self._batch

    @property
    def BATCH(self):
        return self._batch

    @property
    def runfmt(self):
        return self._runfmt

    @property
    def fastq_suffix(self):
        return "_{}.fastq.gz".format(self.read)

    @classmethod
    def reset(cls):
        cls.census = 0

    @property
    def sampleinfo_keys(self):
        return sorted(set([x for x in re.split("[{}/_]", self.runfmt) if x != ""] + ["fastq"]))

    @property
    def sampleinfo(self):
        info = []
        for c in self.sampleinfo_keys:
            info.append(getattr(self, c))
        return ",".join(info)

    def __iter__(self):
        yield 'POP', self.population
        yield 'PU', self.platform_unit
        yield 'SM', self.id
        yield 'BATCH', self.batch


class ReferenceFixtureFile(FixtureFile):
    def __new__(cls, *args, **kwargs):
        obj = super(ReferenceFixtureFile, cls).__new__(cls)
        cls._data_dir = os.path.join(DATA_DIR, "ref")
        cls._ref = {'ref': [], 'scaffolds': [],
                    '_always': ['ERCC_spikes.gb', 'pAcGFP1-N1.fasta']}
        for f in os.listdir(cls._data_dir):
            if "scaffolds" in f:
                cls._ref['scaffolds'].append(f)
            elif "ref" in f:
                cls._ref['ref'].append(f)
            else:
                pass
        return obj

    def __init__(self, path="ref.fa", expanduser=None, *args, **kwargs):
        if isinstance(path, str):
            # Makes custom paths possible
            path = py.path.local(path)
        src = py.path.local(os.path.join(self.data_dir, path.basename))
        super(ReferenceFixtureFile, self).__init__(path=path,
                                                   expanduser=expanduser, src=src, *args, **kwargs)

    @property
    def ref(self):
        return self._ref


class ApplicationFixtureFile(FixtureFile):
    _end = set(["se", "pe"])

    def __init__(self, application, command, version, path=None, expanduser=None, end="se", *args, **kwargs):
        src = py.path.local(os.path.join(DATA_DIR, "applications", application, version, end))
        super(ApplicationFixtureFile, self).__init__(src=src, path=path, expanduser=expanduser, *args, **kwargs)
