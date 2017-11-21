# -*- coding: utf-8 -*-
import os
import re
import py
import itertools
from py._path.local import LocalPath
from pytest_ngsfixtures.os import safe_symlink, safe_copy
from pytest_ngsfixtures.config import sample_conf, get_application_fixture_output, flattened_application_fixture_metadata
from pytest_ngsfixtures import DATA_DIR


class FixtureFile(LocalPath):
    def __new__(cls, *args, **kwargs):
        obj = super(FixtureFile, cls).__new__(cls)
        cls._data_dir = LocalPath(DATA_DIR)
        return obj

    def __init__(self, path=None, expanduser=False, setup=False,
                 src=None, alias=None, copy=False, prefix="s",
                 short_name=False, **kwargs):
        super(FixtureFile, self).__init__(path, expanduser)
        self._prefix = prefix
        self._short = short_name
        self.alias = alias
        if self.alias:
            self.strpath = str(self.path.join(self.alias))
        self._copy = copy
        self.src = src
        self._setup_fn = safe_copy if self._copy else safe_symlink
        if setup:
            self.setup()

    @property
    def full_prefix(self):
        return self.prefix

    @property
    def prefix(self):
        return self._prefix

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, alias):
        if self.short and alias is None:
            self._alias = self.full_prefix
        else:
            self._alias = alias

    @property
    def short(self):
        return self._short

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, src):
        if src is None and not self.isdir():
            src = self.basename
        assert src is not None, "source file must not be None"
        if isinstance(src, str):
            if os.path.isabs(src):
                src = py.path.local(src)
            else:
                src = self.data_dir.join(src)
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
        if self.isdir():
            self._setup_fn(self.path, self.src, self.src.basename)
        else:
            self._setup_fn(self.path, self.src, self.basename)

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def name(self):
        return self.alias if self.alias else self.basename

    @property
    def id(self):
        return self.name

    def __repr__(self):
        return "{} (src: {})".format(self, self.src)


class FixtureFileSet(FixtureFile):
    def __init__(self, path=None, expanduser=False, setup=False,
                 full=True, output=[], **kwargs):
        self._full = full
        self.output = output
        super(FixtureFileSet, self).__init__(path, expanduser, setup, **kwargs)
        assert self.isdir(), "FixtureFileSet output must be a directory"
        assert self.src.isdir(), "FixtureFileSet source must be a directory"

    @property
    def full(self):
        return self._full

    def setup(self):
        for v in self.output:
            if not self.full:
                v = os.path.basename(v)
            self._setup_fn(self.path, self.src.join(v), v)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, output):
        assert isinstance(output, list), "output must be a list"
        self._output = output


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

    def __init__(self, sample="CHS.HG00512", path=None, size="tiny",
                 alias=None, short_name=False, read=1, batch=None,
                 prefix="s", runfmt="{SM}", population=None,
                 platform_unit=None, *args, **kwargs):
        self.sample = sample
        self._size = size
        self.read = read
        self._short = short_name
        self._prefix = prefix
        self.alias = alias
        self._index = self._samples.index(sample)
        self._population = population if population else self._populations[self._index]
        self._platform_unit = platform_unit if platform_unit else self._platform_units[self._index]
        self._batch = batch
        self._runfmt = runfmt

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
        kwargs['src'] = self.data_dir.join(self._size, "{}{}".format(self.sample, self.fastq_suffix))
        super(ReadFixtureFile, self).__init__(path=path, **kwargs)
        if self.alias is not None:
            self.strpath = str(self.path.join(self.fastq))

    @property
    def id(self):
        return self.alias if self.alias else self.sample

    @property
    def sample(self):
        return self._sample

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, alias):
        if self.short and alias is None:
            self._alias = self.full_prefix
        else:
            self._alias = alias

    @sample.setter
    def sample(self, sample):
        assert sample in self._samples, "sample has to be one of {}".format(", ".join(self._samples))
        self._sample = sample

    @property
    def full_prefix(self):
        return "{}{}".format(self.prefix, self.census)

    @property
    def SM(self):
        return self._sample

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
        cls._data_dir = LocalPath(os.path.join(DATA_DIR, "ref"))
        cls._ref = {
            'ref': [],
            'scaffolds': [],
            '_always': [cls._data_dir.join('ERCC_spikes.gb'),
                        cls._data_dir.join('pAcGFP1-N1.fasta')]
        }
        for f in cls._data_dir.visit():
            if "scaffolds" in f.basename:
                cls._ref['scaffolds'].append(f)
            elif "ref" in f.basename:
                cls._ref['ref'].append(f)
            else:
                pass
        return obj

    def __init__(self, path="ref.fa", expanduser=None, src=None, *args, **kwargs):
        if isinstance(path, str):
            # Makes custom paths possible
            path = py.path.local(path)
        if src is None:
            src = py.path.local(os.path.join(self.data_dir, path.basename))
        super(ReferenceFixtureFile, self).__init__(path=path,
                                                   expanduser=expanduser, src=src, *args, **kwargs)

    @property
    def ref(self):
        return self._ref


class ApplicationFixtureFile(FixtureFile):
    _end = set(["se", "pe"])

    def __new__(cls, *args, **kwargs):
        obj = super(ApplicationFixtureFile, cls).__new__(cls)
        cls._data_dir = LocalPath(os.path.join(DATA_DIR, "applications"))
        return obj

    def __init__(self, path, expanduser=None, end="pe", *args, **kwargs):
        if isinstance(path, str):
            path = py.path.local(path)
        kwargs['src'] = self._data_dir.join(end, path.basename)
        super(ApplicationFixtureFile, self).__init__(path=path, expanduser=expanduser, *args, **kwargs)


class ApplicationOutputFixture(FixtureFileSet):
    _end = set(["se", "pe"])

    def __new__(cls, *args, **kwargs):
        obj = super(ApplicationOutputFixture, cls).__new__(cls)
        cls._data_dir = LocalPath(os.path.join(DATA_DIR, "applications"))
        cls._metadata = flattened_application_fixture_metadata()
        return obj

    def __init__(self, application, command, version, path=None,
                 expanduser=None, end="pe", full=True, *args, **kwargs):
        # Src is here a directory
        src = self._data_dir.join(application, version, end)
        # Output holds a list of application outputs
        output = list(get_application_fixture_output(application, command, version, end).values())
        super(ApplicationOutputFixture, self).__init__(src=src, path=path, output=output,
                                                       expanduser=expanduser, full=full, *args, **kwargs)

    @property
    def metadata(self):
        return self._metadata


def fixturefile_factory(path=None, setup=False, **kwargs):
    """Factory function to auto-generate a FixtureFile"""
    kwargs['setup'] = setup
    try:
        application = kwargs.pop("application", None)
        command = kwargs.pop("command", None)
        version = kwargs.pop("version", None)
        ff = ApplicationOutputFixture(application, command, version, path=path, **kwargs)
        return ff
    except TypeError:
        pass
    except AssertionError:
        pass
    except:
        raise
    try:
        ff = ApplicationFixtureFile(path=path, **kwargs)
        return ff
    except AttributeError:
        pass
    except AssertionError:
        pass
    except:
        raise
    try:
        ff = ReferenceFixtureFile(path=path, **kwargs)
        return ff
    except AttributeError:
        pass
    except AssertionError:
        pass
    except:
        raise
    try:
        sample = kwargs.pop("sample", None)
        ff = ReadFixtureFile(path=path, sample=sample, **kwargs)
        return ff
    except AssertionError:
        pass
    except:
        raise
    try:
        ff = FixtureFile(path=path, **kwargs)
        return ff
    except:
        raise


def setup_filetype(path, src=None, copy=False, setup=True, **kwargs):
    """Setup filetype fixture file.

    Wrapper function to setup single filetype fixture.

    Args:
      path (str, py._path.local.LocalPath): :py:`~py._path.local.LocalPath` destination path
      copy (bool): copy test file instead of symlinking

    Returns:
      py._path.local.LocalPath: modified :py:`~py._path.local.LocalPath` with test file setup
    """
    path = fixturefile_factory(path=path, src=src, copy=copy, setup=setup, **kwargs)
    return path


def setup_fileset(path, src, dst=[], copy=False, setup=True, **kwargs):
    """Setup fileset fixture files.

    Wrapper function to setup fileset fixture.

    Args:
      path (py._local.path.LocalPath): :py:`~py._path.local.LocalPath` destination path
      src (list): list of source file names
      path (list): list of destination file names; if empty, use src basenames
      copy (bool): copy test files instead of symlinking

    Returns:
      py._path.local.LocalPath: modified :py:`~py._path.local.LocalPath` with test files setup
    """
    assert isinstance(src, list), "src is not a list"
    assert isinstance(dst, list), "dst is not a list"

    for s, d in itertools.zip_longest(src, dst):
        if d is None:
            d = path.join(os.path.basename(s))
        else:
            if isinstance(d, str):
                if os.path.isabs(d):
                    d = py.path.local(d)
                else:
                    d = path.join(d)
        FixtureFile(path=d, src=s, setup=setup, **kwargs)
    return path
