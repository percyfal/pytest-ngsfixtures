#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_pytest_ngsfixtures
----------------------------------

Tests for `pytest_ngsfixtures` module.
"""


def test_flat(flat):
    l = [x for x in sorted(flat.listdir()) if str(x).endswith(".gz")]
    assert len(l) == 2
    assert str(l[0]).endswith("s1_1.fastq.gz")


def test_sample(sample):
    l = [x for x in sorted(sample.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith(sample.basename + "/s1/s1_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in sample.listdir() if x.isdir()]) == 2


def test_sample_run(sample_run):
    l = [x for x in sorted(sample_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith(sample_run.basename + "/s1/010101_AAABBB11XX/s1_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in sample_run.listdir() if x.isdir()]) == 2


def test_sample_project_run(sample_project_run):
    l = [x for x in sorted(sample_project_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith(sample_project_run.basename + "/s1/p1/010101_AAABBB11XX/s1_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in sample_project_run.listdir() if x.isdir()]) == 2


def test_pop_sample(pop_sample):
    l = [x for x in sorted(pop_sample.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith(pop_sample.basename + "/CHS/CHS.HG00512/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in pop_sample.join("PUR").listdir() if x.isdir()]) == 2


def test_pop_sample_run(pop_sample_run):
    l = [x for x in sorted(pop_sample_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith(pop_sample_run.basename + "/CHS/CHS.HG00512/010101_AAABBB11XX/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in pop_sample_run.join("PUR").listdir() if x.isdir()]) == 2


def test_pop_sample_project_run(pop_sample_project_run):
    l = [x for x in sorted(pop_sample_project_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 14
    assert str(l[0]).endswith(pop_sample_project_run.basename + "/CHS/CHS.HG00512/p1/010101_AAABBB11XX/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in pop_sample_project_run.join("PUR").listdir() if x.isdir()]) == 2


def test_pool_pop_sample(pool_pop_sample):
    l = [x for x in sorted(pool_pop_sample.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith(pool_pop_sample.basename + "/CHS/CHS.pool/CHS.pool_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in pool_pop_sample.join("PUR").listdir() if x.isdir()]) == 1


def test_pool_pop_sample_run(pool_pop_sample_run):
    l = [x for x in sorted(pool_pop_sample_run.visit()) if str(x).endswith(".gz")]
    assert len(l) == 6
    assert str(l[0]).endswith(pool_pop_sample_run.basename + "/CHS/CHS.pool/010101_AAABBB11XX/CHS.pool_010101_AAABBB11XX_1.fastq.gz")
    assert len([x for x in pool_pop_sample_run.join("PUR").listdir() if x.isdir()]) == 1


def test_ref(ref):
    with ref.join("chrom.sizes").open() as fh:
        lines = fh.readlines()
    assert lines[0] == "chr6\t2000000\n"


def test_scaffolds(scaffolds):
    with scaffolds.join("chrom.sizes").open() as fh:
        lines = fh.readlines()
    assert lines[0] == "scaffold1\t1050000\n"
