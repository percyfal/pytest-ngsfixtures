#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_factories
----------------------------------

Tests for `pytest_ngsfixtures.factories` module.
"""
import os
import re
import pytest
from pytest_ngsfixtures import factories
from pytest_ngsfixtures.factories import safe_mktemp, safe_symlink
from pytest_ngsfixtures.config import application_fixtures

# Filetypes
bamfile_realpath = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "pytest_ngsfixtures", "data", "applications", "pe", "PUR.HG00731.tiny.bam"))
PURHG00731 = os.path.join("applications", "pe", "PUR.HG00731.tiny.bam")
PURHG00733 = os.path.join("applications", "pe", "PUR.HG00733.tiny.bam")
PURFILES = [PURHG00731, PURHG00733]
bamfile = PURHG00731
bam = factories.filetype(bamfile, fdir="bamfoo", scope="function", numbered=True)
renamebam = factories.filetype(bamfile, fdir="renamebamfoo", rename=True, outprefix="s", scope="function", numbered=True)


def test_wrong_sample():
    with pytest.raises(factories.SampleException):
        factories.sample_layout(samples=["foo", "bar"])(None, None)


def test_safe_mktemp(tmpdir_factory):
    bn = tmpdir_factory.getbasetemp()
    p = safe_mktemp(tmpdir_factory)
    assert p == bn
    p = safe_mktemp(tmpdir_factory, dirname="foo")
    assert p == bn.join("foo")
    p = safe_mktemp(tmpdir_factory, dirname="foo", numbered=True)
    assert p == bn.join("foo0")
    p = safe_mktemp(tmpdir_factory, dirname=os.curdir)
    assert p == bn
    p = safe_mktemp(tmpdir_factory, dirname="foo/bar")
    assert p == bn.join("foo/bar")
    p = safe_mktemp(tmpdir_factory, dirname="foo/bar", numbered=True)
    assert p == bn.join("foo/bar0")


def test_safe_symlink(tmpdir_factory, bam):
    p = tmpdir_factory.mktemp("safe_symlink")
    # Test using string as input without capturing return
    safe_symlink(p, bamfile, "bar/foo.bar")
    assert str(p).endswith("safe_symlink0")
    # Test using string as input
    l = safe_symlink(p, bamfile, "foo/foo.bar")
    assert str(l).endswith("foo/foo.bar")
    assert l.realpath() == bamfile_realpath
    # Test using localpath as input
    l = safe_symlink(p, bam, "foo.bar")
    assert l.realpath() == bam.realpath()
    assert str(l).endswith("foo.bar")


def test_bam(bam):
    assert not re.search("bamfoo\d+/PUR.HG00731.tiny.bam", str(bam)) is None
    assert bam.realpath() == bamfile_realpath
    assert bam.realpath().exists()


def test_bam_rename(renamebam):
    assert not re.search("renamebamfoo\d+/s.tiny.bam", str(renamebam)) is None
    assert renamebam.realpath() == bamfile_realpath
    assert renamebam.realpath().exists()


@pytest.fixture(scope="function")
def combinedbam(tmpdir_factory, bam, renamebam):
    p = tmpdir_factory.mktemp("combined")
    p.join(bam.basename).mksymlinkto(bam.realpath())
    p.join(renamebam.basename).mksymlinkto(renamebam.realpath())
    return p


def test_combine_fixtures(combinedbam):
    flist = sorted([x for x in combinedbam.visit()])
    assert len(flist) == 2
    assert flist[0].dirname == flist[1].dirname
    flist = sorted([x.basename for x in combinedbam.visit()])
    assert flist == ['PUR.HG00731.tiny.bam', 's.tiny.bam']
    fset = set([str(x.realpath()) for x in combinedbam.visit()])
    assert fset == set([bamfile_realpath])


custom_samples = factories.sample_layout(
    dirname="foo",
    samples=["CHS.HG00512", "YRI.NA19238"],
    platform_units=['bar', 'foobar'],
    paired_end=[True, False],
    use_short_sample_names=False,
    runfmt="{SM}/{SM}_{PU}",
    numbered=False,
    scope="function",
)


def test_custom(custom_samples, ref):
    assert custom_samples.basename == "foo"
    flist = [str(x.basename) for x in custom_samples.visit()]
    assert "CHS.HG00512_bar_1.fastq.gz" in flist
    assert "CHS.HG00512_bar_2.fastq.gz" in flist
    assert "YRI.NA19238_foobar_1.fastq.gz" in flist
    assert "YRI.NA19238_foobar_2.fastq.gz" not in flist


def test_download_url_fail(tmpdir_factory):
    import urllib.request
    bn = tmpdir_factory.mktemp("foo").join("foo.bar")
    with pytest.raises(urllib.error.HTTPError):
        factories.download_sample_file(str(bn), "yuge")


def test_download_url_wrong_size(tmpdir_factory):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar")
    factories.download_sample_file(str(bn), "tiny")
    assert not bn.exists()


def test_download_url(tmpdir_factory, monkeypatch):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar.gz")

    def mockreturn(*args):
        return "https://raw.githubusercontent.com/percyfal/pytest-ngsfixtures/master/pytest_ngsfixtures/data/tiny/CHS.HG00512_1.fastq.gz"
    monkeypatch.setattr(os.path, 'join', mockreturn)
    factories.download_sample_file(str(bn), "yuge")
    import gzip
    with gzip.open(str(bn), 'rb') as fh:
        assert fh.readlines()[0].strip() == b'@ERR016116.1225854/1'


def test_download_url_exists(tmpdir_factory):
    bn = tmpdir_factory.mktemp("foo").join("foo.bar.gz")
    bn.write("foo.bar")
    factories.download_sample_file(str(bn), "yuge")
    assert "foo.bar" == "".join(bn.readlines())


sample_aliases = factories.sample_layout(
    samples=['CHS.HG00512', 'CHS.HG00513', 'CHS.HG00512'],
    sample_aliases=['s1', 's1', 's2'],
    platform_units=['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
    paired_end=[True] * 3,
    dirname="samplealiases",
    runfmt="{SM}/{SM}_{PU}",
    numbered=True,
    scope="function",
)


def test_sample_aliases(sample_aliases):
    d = {str(x.basename): str(x.realpath().basename) for x in sample_aliases.visit() if str(x).endswith("fastq.gz")}
    assert sample_aliases.basename == "samplealiases0"
    assert d["s1_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"
    assert d["s1_020202_AAABBB22XX_1.fastq.gz"] == "CHS.HG00513_1.fastq.gz"
    assert d["s2_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"


def test_fileset_fixture_raises():
    with pytest.raises(AssertionError):
        factories.fileset(src="foo")
    with pytest.raises(AssertionError):
        factories.fileset(src=["foo"], dst="bar")


bamset = factories.fileset(src=PURFILES, fdir="bamset", scope="function")


def test_fileset_fixture(bamset):
    flist = sorted([x.basename for x in bamset.visit() if x.basename != ".lock"])
    assert flist == sorted([os.path.basename(x) for x in PURFILES])

dstfiles = ["foo.fastq.gz", "bar.fastq.gz"]
bamset2 = factories.fileset(src=PURFILES, dst=dstfiles, fdir="bamset2", scope="function")


def test_fileset_fixture_dst(bamset2):
    flist = sorted([x.basename for x in bamset2.visit() if x.basename != ".lock"])
    assert flist == sorted(dstfiles)
    flist = sorted([x.realpath() for x in bamset2.visit() if x.basename != ".lock"])
    assert flist[0] == bamfile_realpath


##############################
# Applications
##############################
# Application test config
fixtures = application_fixtures()


@pytest.fixture(scope="function", autouse=False, params=fixtures,
                ids=["{} {}:{}/{}".format(x[0], x[1], x[2], x[3]) for x in fixtures])
def ao(request, tmpdir_factory):
    app, command, version, end, fmtdict = request.param
    params = {'version': version, 'end': end}
    outputs = [fmt.format(**params) for fmt in fmtdict.values()]
    sources = [os.path.join("applications", app, output) for output in outputs]
    dests = [os.path.basename(src) for src in sources]
    fdir = os.path.join(app, str(version), command, end)
    pdir = safe_mktemp(tmpdir_factory, fdir)
    for src, dst in zip(sources, dests):
        p = safe_symlink(pdir, src, dst)
    return pdir


def test_application_output(ao):
    for p in ao.visit():
        assert p.exists()


def test_application_fixture_params():
    c = application_fixtures(application="samtools")
    assert isinstance(c, list)


def test_call_application_output():
    with pytest.raises(AssertionError):
        factories.application_output("foo", "bar", "0.0")
    factories.application_output("samtools", "samtools_flagstat", "1.2")


appout = factories.application_output("samtools", "samtools_flagstat", "1.2")


def test_factory_application_output(appout):
    assert appout.exists()

appout_dir = factories.application_output("samtools", "samtools_flagstat", "1.2", fdir="samtools/samtools_flagstat")


def test_factory_application_output_fdir(appout_dir):
    assert appout_dir.exists()
    assert "samtools/samtools_flagstat" in str(appout_dir)

# Test pool fixtures; these are not defined by default
kwargs = {
    'samples': ['CHS', 'PUR', 'YRI'],
    'platform_units': ['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
    'populations': ['CHS', 'PUR', 'YRI'],
    'paired_end': [True] * 3,
    'use_short_sample_names': False,
    'numbered': True,
}

pool_pop_sample = factories.sample_layout(
    dirname="pool_pop_sample",
    runfmt="{POP}/{SM}/{SM}_{PU}",
    **kwargs,
)


def test_pool_pop_sample(pool_pop_sample):
    p = pool_pop_sample
    for x in sorted(p.visit()):
        if str(x).endswith(".gz"):
            assert not re.search("tiny/(CHS|PUR|YRI)_\d+.fastq.gz$", str(x.realpath())) is None

pool_pop_sample_aliases = factories.sample_layout(
    dirname="pool_pop_sample_aliases",
    runfmt="{POP}/{SM}/{SM}_{PU}",
    sample_aliases=["CHS.pool", "PUR.pool", "YRI.pool"],
    **kwargs,
)


def test_pool_pop_sample_aliases(pool_pop_sample_aliases):
    p = pool_pop_sample_aliases
    sampleinfo = p.join("sampleinfo.csv")
    assert not re.search(",CHS.pool,", sampleinfo.readlines()[1]) is None
