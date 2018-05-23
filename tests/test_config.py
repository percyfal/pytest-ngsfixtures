#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import shutil
from pytest_ngsfixtures.shell import shell
from pytest_ngsfixtures.config import reflayout, layout, SAMPLES_DIR


@pytest.mark.samples(layout=[2,1])
@pytest.mark.xfail(strict=True)
def test_samples_list(samples):
    pass


@pytest.mark.parametrize("layout,dirname", [(layout['flat'], "data/flat"),
                                            (layout['sample'], "data/sample")])
def test_samples(samples, ref, layout, dirname):
    assert ref.join("scaffolds.fa").exists()
    assert samples.join(list(layout)[0]).exists()


@pytest.mark.ref(dirname="Foo", copy=False)
def test_ref(ref):
    assert ref.join("scaffolds.fa").exists()
    assert ref.join("scaffolds.fa").islink()


@pytest.mark.skipif(shutil.which("bwa") is None, reason="executable bwa not found")
@pytest.mark.skipif(shutil.which("samtools") is None, reason="executable samtools not found")
def test_data(samples, ref):
    shell("bwa index {}".format(ref.join("scaffolds.fa")))
    shell("bwa mem {} {} {} | samtools view -b > {}".format(
        ref.join("scaffolds.fa"),
        samples.join("s1_1.fastq.gz"),
        samples.join("s1_2.fastq.gz"),
        samples.join("s1.bam")
    ))
    assert samples.join("s1.bam").exists()
