# -*- coding: utf-8 -*-
import os
import re
import py
import logging
import itertools
import pytest
from pytest_ngsfixtures.config import conf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make py.path objects?
ROOTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATADIR = os.path.realpath(os.path.join(ROOTDIR, "pytest_ngsfixtures", "data"))
REPO = "https://raw.githubusercontent.com/percyfal/pytest-ngsfixtures/master"
DOWNLOAD_SIZES = ["yuge"]

class ParameterException(Exception):
    pass

class SampleException(Exception):
    pass

ref_dict = {}

for f in os.listdir(os.path.join(DATADIR, "ref")):
    if f in ("Makefile", "Snakefile.test"):
        continue
    ref_dict[f] = os.path.join(DATADIR, "ref", f)

ref_always=['ERCC_spikes.gb', 'pAcGFP1-N1.fasta']


def check_samples(samples):
    """Check the sample names are ok"""
    if not all(x in conf.SAMPLES for x in samples):
        raise SampleException("invalid sample name: choose from {}".format(conf.SAMPLES))


def get_config(request):
    """Return a dictionary with config options."""
    config = {}
    options = [
        'size',
    ]
    for option in options:
        option_name = 'ngs_' + option
        conf = request.config.getoption(option_name) or \
            request.config.getini(option_name)
        config[option] = conf
    return config


def _download_sample_file(fn, size):
    """Download sample file if it doesn't yet exist

    Setup urllib connection and download data file.
    """
    if not size in DOWNLOAD_SIZES:
        return
    if os.path.exists(fn):
        return
    else:
        import urllib.request
        import shutil
        logger.info("File '{}' doesn't exist; downloading it from git repo to local pytest_ngsfixtures installation location".format(fn))
        url = os.path.join(REPO, os.path.relpath(fn, ROOTDIR))
        try:
            with urllib.request.urlopen(url) as response, open(fn, 'wb') as fh:
                shutil.copyfileobj(response, fh)
        except Exception as e:
            logger.error("Downloading '{}' failed: {}".format(url, e))
            raise


def safe_symlink(p, src, dst):
    """Safely make symlink.

    Make symlink from src to dst in LocalPath p. If src, dst are
    strings, they will be joined to p, assuming they are relative to
    p. If src, dst are LocalPath instances, they are left alone since
    LocalPath objects are always absolute paths.

    Params:
      p (LocalPath): path in which link is setup
      src (str, LocalPath): source file that link points to. If string, assume relative to pytest_ngsfixtures data directory
      dst (str, LocalPath): link destination name. If string, assume relative to path and concatenate; else leave alone

    Returns:
      dst (LocalPath): link name
    """
    if isinstance(src, str):
        if not os.path.isabs(src):
            src = os.path.join(DATADIR, src)
        src = py.path.local(src)
    if dst is None:
        dst = src.basename
    if isinstance(dst, str):
        dst = p.join(dst)
    if not dst.check(link=1):
        dst.dirpath().ensure(dir=True)
        dst.mksymlinkto(src)
    else:
        logger.warn("link {dst} -> {src} already exists! skipping...".format(src=src, dst=dst))
    return dst


def safe_mktemp(tmpdir_factory, dirname=None, **kwargs):
    """Safely make directory"""
    if dirname is None:
        return tmpdir_factory.getbasetemp()
    else:
        p = tmpdir_factory.getbasetemp().join(dirname)
        if kwargs.get("numbered", False):
            p = tmpdir_factory.mktemp(dirname)
        else:
            if not p.check(dir=1):
                p = tmpdir_factory.mktemp(dirname, numbered=False)
        return p



def sample_layout(
        runfmt = "{SM}",
        sample_prefix="s",
        use_short_sample_names = True,
        read1_suffix="_1.fastq.gz",
        read2_suffix="_2.fastq.gz",
        dirname=None,
        sampleinfo=True,
        combinator=itertools.zip_longest,
        sample_aliases=[],
        samples=[None],
        platform_units=[None],
        batches=[None],
        populations=[None],
        paired_end=[True],
        **kwargs
):
    """Fixture factory for pytest-ngsfixtures sample layouts.

    Generates a directory structure by linking to data files in
    pytest-ngsfixtures data directory. A certain amount of generality
    is allowed in that platform units and batches can be named at
    will. Short sample names can also be used.

    Briefly, sample file names are generated by combining labels in
    the lists **samples** (SM), **platform_units** (PU), **batches**
    (BATCH), and **populations** (POP), and formatting the directory
    structure following the *runfmt* format specification. For
    instance, with samples = ["CHR.HG00512"], populations=None,
    batches=None, platform_units=["010101_AAABBB11XX"], and
    runfmt="{SM}/{PU}/{SM}_{PU}", input files will be organized as
    "CHR.HG00512/010101_AAABBB11XX/CHR.HG00512_010101_AAABBB11XX_1.fastq.gz"
    and similarly for the second read.

    Usage:

    .. code-block:: python

       from pytest_ngsfixtures import factories
       my_layout = factories.sample_layout(
           dirname="foo",
           samples=["CHR.HG00512"],
           platform_units=["010101_AAABBB11XX"],
           populations=["CHR"],
           batches=["batch1"],
           runfmt="{POP}/{SM}/{BATCH}/{PU}/{SM}_{PU}",
       )


    Params:
      runfmt (str): run format string
      sample_prefix (str): sample prefix for short names
      use_short_sample_names (bool): use short sample names
      read1_suffix (str): read1 suffix
      read2_suffix (str): read2 suffix
      dirname (str): data directory name
      sampleinfo (bool): create sampleinfo file
      combinator (fun): function to combine sample, platform unit, batch, population labels
      sample_aliases (list): list of sample alias names
      samples (list): list of sample names
      platform_units (list): list of platform units
      batches (list): list of batch (project) names
      populations (list): list of population names
      paired_end (list): list of booleans indicating if a sample run is paired end (True) or single end (False)

    Returns:
      p (py.path.local): tmp directory with sample layout setup

    """
    @pytest.fixture(autouse=False)
    def sample_layout_fixture(request, tmpdir_factory):
        """Sample layout fixture. Setup sequence input files according to a
        specified sample organization"""

        check_samples(samples)
        config = get_config(request)
        _samples = samples
        _pop = populations
        _batches = batches
        _pu = platform_units
        _pe = paired_end
        _aliases = sample_aliases
        _keys = ['POP', 'PU', 'SM', 'BATCH', 'PE']
        _param_names = ['populations', 'platform_units', 'samples', 'batches', 'paired_end']
        _keys_to_param_names = dict(zip(_keys, _param_names))
        _param_dict = dict(zip(_keys, (_pop, _pu, _samples, _batches, _pe)))
        _layout = [dict(zip(_keys, p)) for p in combinator(_pop, _pu, _samples, _batches, _pe)]
        _sample_counter = 1
        _sample_map = {}
        _sampleinfo = []
        p = safe_mktemp(tmpdir_factory, dirname, **kwargs)
        for l in _layout:
            srckeys = l.copy()
            if not l["SM"] in _sample_map.keys():
                _sample_map[l["SM"]] = "{}{}".format(sample_prefix, _sample_counter)
                _sample_counter = _sample_counter + 1
            if use_short_sample_names:
                l['SM'] = _sample_map[l['SM']]
            if len(sample_aliases) > 0:
                l['SM'] = sample_aliases.pop()
            src = os.path.join(DATADIR, config['size'], srckeys['SM'] + "_1.fastq.gz")
            _download_sample_file(src, config['size'])
            safe_symlink(p, os.path.join(DATADIR, config['size'], srckeys['SM'] + "_1.fastq.gz"),
                    runfmt.format(**l) + read1_suffix)
            if l['PE']:
                safe_symlink(p, os.path.join(DATADIR, config['size'], srckeys['SM'] + "_2.fastq.gz"),
                        runfmt.format(**l) + read2_suffix)

        if sampleinfo:
            outkeys = set([x for x in re.split("[{}/_]", runfmt) if x != ""] + ["fastq"])
            if any(len(x[0]) != len(x[1]) for x in itertools.combinations((_param_dict[y] for y in outkeys if not y == "fastq"), 2)):
                raise ParameterException("all parameters {} must be of equal length for sampleinfo file".format(",".join(_keys_to_param_names[y] for y in outkeys if not y == "fastq")))
            info = [",".join(outkeys)]
            for l in _layout:
                logger.debug("updating layout: {}".format(l))
                l['fastq'] = runfmt.format(**l) + read1_suffix
                info.append(",".join([l[k] for k in outkeys]))
                if l['PE']:
                    l['fastq'] = runfmt.format(**l) + read2_suffix
                    info.append(",".join([l[k] for k in outkeys]))
            info.append("\n")
            p.join("sampleinfo.csv").write("\n".join(info))
        # Alternatively print as debug
        if request.config.option.ngs_show_fixture:
            logger.info("sample_layout")
            logger.info("-------------")
            for x in sorted(p.visit()):
                logger.info(str(x))
        return p
    return sample_layout_fixture


def reference_layout(label="ref", dirname="ref", **kwargs):
    """
    Fixture factory for reference layouts.

    Params:
      label (str): ref or scaffolds layout
      dirname (str): reference directory name


    """
    @pytest.fixture(scope=kwargs.get("scope", "session"), autouse=kwargs.get("autouse", False))
    def reference_layout_fixture(request, tmpdir_factory):
        """Reference layout fixture. Setup the one-chromosome reference files
        or scaffold reference files in a separate directory"""
        p = safe_mktemp(tmpdir_factory, dirname, **kwargs)
        for dst, src in ref_dict.items():
            if dst in ref_always:
                safe_symlink(p, src, dst)
            if not label in dst:
                continue
            if dst.endswith("chrom.sizes"):
                dst = "chrom.sizes"
            safe_symlink(p, src, dst)
        if request.config.option.ngs_show_fixture:
            logger.info("'{}' reference layout".format(label))
            logger.info("------------------------------------")
            for x in sorted(p.visit()):
                logger.info(str(x))
        return p
    return reference_layout_fixture


def filetype(src, dst=None, fdir=None, rename=False, outprefix="test", inprefix=['PUR.HG00731', 'PUR.HG00733'], **kwargs):
    """Fixture factory for file types. This factory is atomic in that it
    generates one fixture for one file.

    Params:
      src (str): fixture file name source
      dst (str): fixture file name destination; link name
      fdir (str): fixture output directory
      rename (bool): rename fixture links
      outprefix (str): output prefix
      inprefix (list): list of input prefixes to substitute
      kwargs (dict): keyword arguments

    """
    dst = os.path.basename(src) if dst is None else dst
    if rename:
        pat = "(" + "|".join(inprefix) + ")"
        dst = re.sub(pat, outprefix, dst)
    @pytest.fixture(scope=kwargs.get("scope", "function"), autouse=kwargs.get("autouse", False))
    def filetype_fixture(request, tmpdir_factory):
        """Filetype fixture"""
        p = safe_mktemp(tmpdir_factory, fdir, **kwargs)
        p = safe_symlink(p, src, dst)
        if request.config.option.ngs_show_fixture:
            logger.info("filetype fixture content")
            logger.info("------------------------")
            logger.info(str(p))
        return p
    return filetype_fixture


def fileset(src, dst=None, fdir=None, **kwargs):
    """
    Fixture factory to generate filesets.

    Params:
      src (list): list of sources
      dst (list): list of destination; if None, use src basename
      fdir (:obj:`str` or :obj:`py._path.local.LocalPath`): output directory

    Returns:
      func: a fixture function
    """
    assert isinstance(src, list), "not a list"
    assert dst is None or isinstance(dst, list), "not a list"
    if dst is None:
        dst = [None]
    @pytest.fixture(scope=kwargs.get("scope", "function"), autouse=kwargs.get("autouse", False))
    def fileset_fixture(request, tmpdir_factory):
        """Fileset factory

        Setup a set of files

        Params:
          request (FixtureRequest): fixture request object
          tmpdir_factory (py.path.local): fixture request object

        Returns:
          :obj:`py._path.local.LocalPath`: output directory in which the files reside
        """
        p = safe_mktemp(tmpdir_factory, fdir, **kwargs)
        for s, d in itertools.zip_longest(src, dst):
            safe_symlink(p, s, d)
        if request.config.option.ngs_show_fixture:
            logger.info("fileset fixture content")
            logger.info("-----------------------")
            for x in sorted(p.visit()):
                logger.info(str(x))
        return p
    return fileset_fixture



__all__ = ('sample_layout', 'reference_layout', 'filetype', 'fileset')
