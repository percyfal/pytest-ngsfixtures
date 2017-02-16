#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_factories
----------------------------------

Tests for `pytest_ngsfixtures.factories` module.
"""
import os
import py
import pytest
from pytest_ngsfixtures import factories
from pytest_ngsfixtures.factories import safe_mktemp, safe_symlink
from pytest_ngsfixtures.filetypes import *

# Filetypes
bamfile = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "pytest_ngsfixtures", "data", "applications", "PUR.HG00731.bam"))
bam = factories.filetype(bamfile, fdir="bamfoo")
renamebam = factories.filetype(bamfile, fdir="renamebamfoo", rename=True, outprefix="s")


def test_wrong_sample():
    with pytest.raises(factories.SampleException):
        factories.sample_layout(samples=["foo", "bar"])(None, None)


def test_safe_mktemp(tmpdir_factory):
    bn = tmpdir_factory.getbasetemp()
    p = safe_mktemp(tmpdir_factory)
    assert str(p) == str(bn)
    p = safe_mktemp(tmpdir_factory, dirname="foo")
    assert p.basename == "foo"
    p = safe_mktemp(tmpdir_factory, dirname="foo", numbered=True)
    assert p.basename == "foo0"


def test_safe_symlink(tmpdir_factory, bam):
    p = tmpdir_factory.mktemp("safe_symlink")
    # Test using string as input without capturing return
    safe_symlink(p, bamfile, "bar/foo.bar")
    assert str(p).endswith("safe_symlink0")
    # Test using string as input
    l = safe_symlink(p, bamfile, "foo/foo.bar")
    assert str(l).endswith("foo/foo.bar")
    assert l.realpath() == bamfile
    # Test using localpath as input
    l = safe_symlink(p, bam, "foo.bar")
    assert l.realpath() == bam.realpath()
    assert str(l).endswith("foo.bar")
    

def test_bam(bam):
    assert str(bam).endswith("bamfoo/PUR.HG00731.bam")
    assert bam.realpath() == bamfile

def test_bam_rename(renamebam):
    assert str(renamebam).endswith("renamebamfoo/s.bam")
    assert renamebam.realpath() == bamfile

    
@pytest.fixture
def combinedbam(tmpdir_factory, bam, renamebam):
    p = tmpdir_factory.mktemp("combined")
    p.join(bam.basename).mksymlinkto(bam.realpath())
    p.join(renamebam.basename).mksymlinkto(renamebam.realpath())
    return p

def test_combine_fixtures(combinedbam):
    flist = sorted([x.basename for x in combinedbam.visit()])
    assert flist == ['PUR.HG00731.bam', 's.bam']
    fset = set([str(x.realpath()) for x in combinedbam.visit()])
    assert fset == set([bamfile])


@pytest.mark.parametrize("data", filetypes[0:2])
def test_filetypes(data):
    assert data in filetypes[0:2]


custom_samples = factories.sample_layout(
    dirname="foo",
    samples=["CHS.HG00512", "YRI.NA19238"],
    platform_units=['bar', 'foobar'],
    paired_end=[True, False],
    use_short_sample_names=False,
    runfmt="{SM}/{SM}_{PU}",
    numbered=False,
)

def test_custom(custom_samples, ref):
    assert custom_samples.basename == "foo"
    flist = [str(x.basename) for x in custom_samples.visit()]
    assert "CHS.HG00512_bar_1.fastq.gz" in flist
    assert "CHS.HG00512_bar_2.fastq.gz" in flist
    assert "YRI.NA19238_foobar_1.fastq.gz" in flist
    assert "YRI.NA19238_foobar_2.fastq.gz" not in flist



sample_aliases = factories.sample_layout(
    samples = ['CHS.HG00512', 'CHS.HG00513', 'CHS.HG00512'],
    sample_aliases = ['s1', 's1', 's2'],
    platform_units =['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
    paired_end = [True] * 3,
    dirname="samplealiases",
    runfmt="{SM}/{SM}_{PU}",
    numbered=True,
 )


def test_sample_aliases(sample_aliases):
    d = {str(x.basename):str(x.realpath().basename) for x in sample_aliases.visit() if str(x).endswith("fastq.gz")}
    assert sample_aliases.basename == "samplealiases0"
    assert d["s1_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"
    assert d["s1_020202_AAABBB22XX_1.fastq.gz"] == "CHS.HG00513_1.fastq.gz"
    assert d["s2_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"
