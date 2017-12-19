# -*- coding: utf-8 -*-
import os
import re
import py
import itertools
from py._path.local import LocalPath
from pytest_ngsfixtures.os import safe_symlink, safe_copy
from pytest_ngsfixtures.config import sample_conf, get_application_fixture_output
from pytest_ngsfixtures import DATA_DIR


class FixtureFile(LocalPath):
    """Class that represents test file and source file locations. It
    extends :py:class:`~py._path.local.LocalPath` by adding a number
    of attributes.

    The __new__ constructor adds the _data_dir attribute, which is a
    (tentative) source data directory. Unless the provided src
    parameter is a full path, the _data_dir is where the class will
    look for input files

    Args:
      path (str, py._path.local.LocalPath): test file path
      src (str, py._path.local.LocalPath): src file path
      setup (bool): setup test file on the fly
      alias (str): alias test file name
      copy (bool): copy src file to test file
      prefix (str): prefix for short file output
      short_name (bool): use short names instead of full output names
      ignore_errors (bool): ignore errors should target file exist

    Keyword Args:
      expanduser (bool): expand tilde
    """
    def __new__(cls, *args, **kwargs):
        obj = super(FixtureFile, cls).__new__(cls)
        cls._data_dir = LocalPath(DATA_DIR)
        return obj

    def __init__(self, path=None, src=None, setup=False, alias=None,
                 copy=False, prefix="s", short_name=False,
                 ignore_errors=False, **kwargs):
        super(FixtureFile, self).__init__(path, kwargs.get("expanduser", False))
        self._prefix = prefix
        self._short = short_name
        self.alias = alias
        if self.alias:
            self.strpath = str(self.path.join(self.alias))
        self._copy = copy
        self.src = src
        self._ignore_errors = ignore_errors
        self._setup_fn = safe_copy if self._copy else safe_symlink
        if setup:
            self.setup()

    @property
    def full_prefix(self):
        """Get full prefix path"""
        return self.prefix

    @property
    def prefix(self):
        """Get prefix"""
        return self._prefix

    @property
    def alias(self):
        """Get alias"""
        return self._alias

    @alias.setter
    def alias(self, alias):
        """Set alias. If alias is None and short names are requested, set to full_prefix"""
        if self.short and alias is None:
            self._alias = self.full_prefix
        else:
            self._alias = alias

    @property
    def short(self):
        """Get short attribute, indicating whether or not to use short names."""
        return self._short

    @property
    def src(self):
        """Get src path"""
        return self._src

    @src.setter
    def src(self, src):
        """Set src path. Assert that src exists and is not None"""
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
        """Get path"""
        if self.isdir():
            return self
        else:
            return py.path.local(self.dirname)

    def setup(self):
        """Setup test file by copying or via symlink from self.src to self."""
        if self.isdir():
            self._setup_fn(self.path, self.src, self.src.basename, self.ignore_errors)
        else:
            self._setup_fn(self.path, self.src, self.basename, self.ignore_errors)

    @property
    def data_dir(self):
        """Get data directory."""
        return self._data_dir

    @property
    def ignore_errors(self):
        """Ignore errors on setup"""
        return self._ignore_errors

    @property
    def name(self):
        """Get name"""
        return self.alias if self.alias else self.basename

    @property
    def id(self):
        """Alias for self.name"""
        return self.name

    def __repr__(self):
        return "{} (src: {})".format(self, self.src)


class FixtureFileSet(FixtureFile):
    """Class that represents test file and source file sets.

    Args:
      path (str, :py:class:`py._path.local.LocalPath`): test output path; must be a directory
      full (bool): use full path names. If False, use output basenames.
      output (list): list of output file names that will be concatenated to path

    Keyword Args:
      src (str, :py:class:`py._path.local.LocalPath`): src input path; must be a directory

    For full list of keyword arguments, see :py:class:`~pytest_ngsfixtures.file.FixtureFile`.
    """
    def __init__(self, path, full=True, output=[], **kwargs):
        self._full = full
        self.output = output
        super(FixtureFileSet, self).__init__(path, **kwargs)
        assert self.isdir(), "FixtureFileSet output must be a directory"
        assert self.src.isdir(), "FixtureFileSet source must be a directory"

    @property
    def full(self):
        return self._full

    def setup(self):
        """Setup test files"""
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
    """Class that represents read test files.

    The class constructor sets a census attribute that keeps track of
    the number of objects.

    The constructor sets the data directory to the base data directory
    joined with the size.

    Args:
      sample (str): sample name
      size (str): sequence file size
      read (int): read number (1 or 2)
      batch (str): batch name
      runfmt (str): python miniformat string that represents formatted fastq output file. Can contain keys SM, PU, POP, BATCH.
      population (str): population name
      platform_unit (str): platform_unit name

    Keyword Args:
      path (str, :py:class:`py._path.local.LocalPath`): test output path
      alias (str): alias output name
      short_name (bool): use short output names, prefixed by prefix and numbered by class census
      prefix (str): short name prefix

    For full list of keyword arguments, see :py:class:`~pytest_ngsfixtures.file.FixtureFile`.
    """
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

    def __init__(self, sample="CHS.HG00512", size="tiny", read=1,
                 batch=None, runfmt="{SM}", population=None,
                 platform_unit=None, *args,
                 **kwargs):
        self.sample = sample
        self.read = read
        self._size = size
        setup = kwargs.get("setup", False)
        kwargs['src'] = self.data_dir.join(self._size, "{}{}".format(self.sample, self.fastq_suffix))
        kwargs['setup'] = False
        super(ReadFixtureFile, self).__init__(**kwargs)
        self._index = self._samples.index(sample)
        self._population = population if population else self._populations[self._index]
        self._platform_unit = platform_unit if platform_unit else self._platform_units[self._index]
        self._batch = batch
        self._runfmt = runfmt
        # Reset path now that all info is in place
        path = kwargs.get("path", None)
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
        self.strpath = str(path)
        if setup:
            self.setup()

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
        return self.id

    @property
    def full_prefix(self):
        return "{}{}".format(self.prefix, self.census)

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
    """Class that represents reference test files.

    The class constructor sets the data directory to the reference
    data file directory. In addition, the reference data files are
    stored in a dictionary where 'ref' and 'scaffold' reference data
    sets are partitioned by corresponding keys.

    Args:
      path (str, py._path.local.LocalPath): test file path
      src (str, py._path.local.LocalPath): src file path

    """
    def __new__(cls, *args, **kwargs):
        obj = super(ReferenceFixtureFile, cls).__new__(cls)
        cls._data_dir = LocalPath(os.path.join(str(DATA_DIR), "ref"))
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

    def __init__(self, path="ref.fa", src=None, *args, **kwargs):
        if isinstance(path, str):
            # Makes custom paths possible
            path = py.path.local(path)
        if src is None:
            src = py.path.local(os.path.join(str(self.data_dir), path.basename))
        super(ReferenceFixtureFile, self).__init__(path=path, src=src,
                                                   *args, **kwargs)

    @property
    def ref(self):
        return self._ref


class ApplicationFixtureFile(FixtureFile):
    """Class that represents application test files.

    The class constructor sets the data directory to the applications
    data file directory.

    Args:
      path (str, py._path.local.LocalPath): test file path
      end (str): paired end ("pe") or single end ("se")

    """
    _end = set(["se", "pe"])

    def __new__(cls, *args, **kwargs):
        obj = super(ApplicationFixtureFile, cls).__new__(cls)
        cls._data_dir = LocalPath(os.path.join(str(DATA_DIR), "applications"))
        return obj

    def __init__(self, path, end="pe", *args, **kwargs):
        if isinstance(path, str):
            path = py.path.local(path)
        try:
            if not kwargs['src'].exists():
                kwargs['src'] = self._data_dir.join(end, path.basename)
        except:
            kwargs['src'] = self._data_dir.join(end, path.basename)
        super(ApplicationFixtureFile, self).__init__(path=path, *args, **kwargs)


class ApplicationOutputFixture(FixtureFileSet):
    """Class that represents application outputs.

    The class constructor sets the data directory to the applications
    data file directory.

    Args:
      application (str): application name
      command (str): application command name
      version (str): version number as string
      end (str): paired end ("pe") or single end ("se")
      path (str, py._path.local.LocalPath): test file path

    """
    _end = set(["se", "pe"])

    def __new__(cls, *args, **kwargs):
        obj = super(ApplicationOutputFixture, cls).__new__(cls)
        cls._data_dir = LocalPath(os.path.join(str(DATA_DIR), "applications"))
        return obj

    def __init__(self, application, command, version, end="pe",
                 path=None, *args, **kwargs):
        # Src is here a directory
        src = self._data_dir.join(application, version, end)
        # Output holds a list of application outputs
        output = list(get_application_fixture_output(application, command, version, end).values())
        super(ApplicationOutputFixture, self).__init__(src=src, path=path, output=output,
                                                       *args, **kwargs)


def fixturefile_factory(path=None, setup=False, **kwargs):
    """Factory function to auto-generate a FixtureFile.

    Args:
      path (str, py._path.local.LocalPath): test file destination path
      setup (bool): setup test file creation on the fly
    """
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

    Example:

      .. code-block:: python

         import py
         from pytest_ngsfixtures.file import setup_filetype

         p = py.path.local()
         p = setup_fileset(path=p.join('s.bam'), src="/path/to/s.bam")

    Args:
      path (str, py._path.local.LocalPath): :py:class:`~py._path.local.LocalPath` destination path
      src (str, py._path.local.LocalPath): source file location
      copy (bool): copy test file instead of symlinking
      setup (bool): setup test file on the fly

    Returns:
      py._path.local.LocalPath: modified :py:class:`~py._path.local.LocalPath` with test file setup
    """
    path = fixturefile_factory(path=path, src=src, copy=copy, setup=setup, **kwargs)
    return path


def setup_fileset(path, src, dst=[], copy=False, setup=True, **kwargs):
    """Setup fileset fixture files.

    Wrapper function to setup fileset fixture.

    Example:

      .. code-block:: python

         import py
         from pytest_ngsfixtures.file import setup_fileset

         p = py.path.local()
         p = setup_fileset(path=p, src=["/path/to/s.bam", "path/to/s.bai"], dst=['s.bam', 's.bam.bai'])

    Args:
      path (py._local.path.LocalPath): :py:class:`~py._path.local.LocalPath` destination path
      src (list): list of source file names
      path (list): list of destination file names; if empty, use src basenames
      copy (bool): copy test files instead of symlinking
      setup (bool): setup test files on the fly

    Returns:
      py._path.local.LocalPath: modified :py:class:`~py._path.local.LocalPath` with test files setup
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
