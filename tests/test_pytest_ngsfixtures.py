#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_ngsfixtures
----------------------------------

Tests for `pytest_ngsfixtures` module.
"""
import os
import pytest
from pytest_ngsfixtures import factories

custom_samples = factories.sample_layout(
    dirname="foo",
    samples=["CHS.HG00512", "YRI.NA19238"],
    platform_units=['bar', 'foobar'],
    paired_end=[True, False],
    use_short_sample_names=False,
    runfmt="{SM}/{SM}_{PU}",
    numbered=False,
)

sample_aliases = factories.sample_layout(
    samples = ['CHS.HG00512', 'CHS.HG00513', 'CHS.HG00512'],
    sample_aliases = ['s1', 's1', 's2'],
    platform_units =['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
    paired_end = [True] * 3,
    dirname="samplealiases",
    runfmt="{SM}/{SM}_{PU}",
 )


def test_sample_aliases(sample_aliases):
    d = {str(x.basename):str(x.realpath().basename) for x in sample_aliases.visit() if str(x).endswith("fastq.gz")}
    assert d["s1_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"
    assert d["s1_020202_AAABBB22XX_1.fastq.gz"] == "CHS.HG00513_1.fastq.gz"
    assert d["s2_010101_AAABBB11XX_1.fastq.gz"] == "CHS.HG00512_1.fastq.gz"


def test_custom(custom_samples, ref):
    assert custom_samples.basename == "foo"
    flist = [str(x.basename) for x in custom_samples.visit()]
    assert "CHS.HG00512_bar_1.fastq.gz" in flist
    assert "CHS.HG00512_bar_2.fastq.gz" in flist
    assert "YRI.NA19238_foobar_1.fastq.gz" in flist
    assert "YRI.NA19238_foobar_2.fastq.gz" not in flist



def test_wrong_sample():
    with pytest.raises(factories.SampleException):
        factories.sample_layout(samples=["foo", "bar"])(None, None)


def test_flat(flat):
    l = [x for x in sorted(flat.listdir()) if str(x).endswith(".gz")]
    assert len(l) == 2
    assert str(l[0]).endswith("s1_1.fastq.gz")


def test_sample(sample):
    l = [x for x in sorted(sample.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith("sample0/s1/s1_010101_AAABBB11XX_1.fastq.gz")


def test_sample_run(sample_run):
    l = [x for x in sorted(sample_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith("sample_run0/s1/010101_AAABBB11XX/s1_010101_AAABBB11XX_1.fastq.gz")


def test_sample_project_run(sample_project_run):
    l = [x for x in sorted(sample_project_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith("sample_project_run0/s1/p1/010101_AAABBB11XX/p1_010101_AAABBB11XX_1.fastq.gz")


def test_pop_sample(pop_sample):
    l = [x for x in sorted(pop_sample.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith("pop_sample0/CHS/CHS.HG00512/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")


def test_pop_sample_run(pop_sample_run):
    l = [x for x in sorted(pop_sample_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith("pop_sample_run0/CHS/CHS.HG00512/010101_AAABBB11XX/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")


def test_pop_sample_project_run(pop_sample_project_run):
    l = [x for x in sorted(pop_sample_project_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith("pop_project_sample_run0/CHS/CHS.HG00512/p1/010101_AAABBB11XX/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")


def test_ref(ref):
    with ref.join("chrom.sizes").open() as fh:
        lines = fh.readlines()
    assert lines[0] == "chr6\t2000000\n"


def test_scaffolds(scaffolds):
    with scaffolds.join("chrom.sizes").open() as fh:
        lines = fh.readlines()
    assert lines[0] == "scaffold1\t1050000\n"
