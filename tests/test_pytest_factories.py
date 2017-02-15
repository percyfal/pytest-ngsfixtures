#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_factories
----------------------------------

Tests for `pytest_ngsfixtures.factories` module.
"""
import os
import pytest
from pytest_ngsfixtures import factories


def test_wrong_sample():
    with pytest.raises(factories.SampleException):
        factories.sample_layout(samples=["foo", "bar"])(None, None)


bam = factories.filetype("bamfoo", os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "pytest_ngsfixtures", "data", "applications", "PUR.HG00731.bam")))

def test_bam(bam):
    flist = [str(x.basename) for x in bam.visit()]
    assert flist == ['PUR.HG00731.bam']


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



