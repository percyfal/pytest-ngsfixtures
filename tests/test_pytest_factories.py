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
from pytest_ngsfixtures.os import safe_symlink, safe_mktemp
from pytest_ngsfixtures.config import flattened_application_fixture_metadata


def test_wrong_sample(tmpdir, monkeypatch):
    monkeypatch.setattr('pytest_ngsfixtures.factories.safe_mktemp',
                        lambda *args, **kwargs: tmpdir)
    with pytest.raises(AssertionError):
        factories.sample_layout(samples=["foo", "bar"])(None, None)


def test_bam(bam, bamfile):
    assert not re.search("bamfoo\d+/PUR.HG00731.tiny.bam", str(bam)) is None
    assert bam.realpath() == bamfile.realpath()
    assert bam.realpath().exists()


def test_copy_bam(bam_copy, bamfile):
    assert not re.search("bamfoo\d+/PUR.HG00731.tiny.bam", str(bam_copy)) is None
    assert bam_copy.computehash() == bamfile.computehash()
    assert bam_copy.realpath().exists()


def test_bam_rename(renamebam, bamfile):
    assert not re.search("renamebamfoo\d+/s.tiny.bam", str(renamebam)) is None
    assert renamebam.realpath() == bamfile.realpath()
    assert renamebam.realpath().exists()


def test_copy_bam_rename(renamebam_copy, bamfile):
    assert not re.search("renamebamfoo\d+/s.tiny.bam", str(renamebam_copy)) is None
    assert renamebam_copy.computehash() == bamfile.computehash()
    assert renamebam_copy.realpath().exists()


@pytest.fixture(scope="function")
def combinedbam(tmpdir_factory, bam, renamebam):
    p = tmpdir_factory.mktemp("combined")
    p.join(bam.basename).mksymlinkto(bam.realpath())
    p.join(renamebam.basename).mksymlinkto(renamebam.realpath())
    return p


def test_combine_fixtures(combinedbam, bamfile):
    flist = sorted([x for x in combinedbam.visit()])
    assert len(flist) == 2
    assert flist[0].dirname == flist[1].dirname
    flist = sorted([x.basename for x in combinedbam.visit()])
    assert flist == ['PUR.HG00731.tiny.bam', 's.tiny.bam']
    fset = set([str(x.realpath()) for x in combinedbam.visit()])
    assert fset == set([bamfile.realpath()])


custom_samples = factories.sample_layout(
    dirname="foo",
    sample=["CHS.HG00512", "YRI.NA19238"],
    platform_unit=['bar', 'foobar'],
    paired_end=[True, False],
    short_name=False,
    runfmt="{SM}/{SM}_{PU}",
    numbered=False,
    scope="function",
)


def test_custom(custom_samples):
    assert custom_samples.basename == "foo"
    flist = [str(x.basename) for x in custom_samples.visit()]
    assert "CHS.HG00512_bar_1.fastq.gz" in flist
    assert "CHS.HG00512_bar_2.fastq.gz" in flist
    assert "YRI.NA19238_foobar_1.fastq.gz" in flist
    assert "YRI.NA19238_foobar_2.fastq.gz" not in flist


sample_aliases = factories.sample_layout(
    sample=['CHS.HG00512', 'CHS.HG00513', 'CHS.HG00512'],
    alias=['s1', 's1', 's2'],
    platform_unit=['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
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


def test_fileset_fixture(bamset, PURFILES):
    flist = sorted([x.basename for x in bamset.visit() if x.basename != ".lock"])
    assert flist == sorted([x.basename for x in PURFILES])


def test_fileset_fixture_dst(bamset2, dstfiles, bamfile):
    flist = sorted([x.basename for x in bamset2.visit() if x.basename != ".lock"])
    assert flist == sorted(dstfiles)
    flist = sorted([x.realpath() for x in bamset2.visit() if x.basename != ".lock"])
    assert flist[0] == bamfile.realpath()


##############################
# Applications
##############################
# Application test config
fixtures = flattened_application_fixture_metadata()


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
        safe_symlink(pdir, src, dst)
    return pdir


def test_application_output(ao):
    for p in ao.visit():
        assert p.exists()


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
