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


@pytest.mark.samples(copy=False)
@pytest.mark.parametrize("name,layout,dirname", [[k, v, k] for k, v in layout.items()],
                         ids=[k for k in list(layout)])
def test_layouts(samples, name, layout, dirname):
    samples_ind =  ['CHS.HG00512', 'PUR.HG00731', 'PUR.HG00733', 'YRI.NA19238', 'CHS.HG00513', 'YRI.NA19239']
    samples_pool = ['CHS', 'PUR', 'YRI']
    if name == "flat":
        assert sorted(['s1_2.fastq.gz', 's1_1.fastq.gz']) == sorted([x.basename for x in samples.listdir()])
    elif name == "sample":
        assert sorted(['CHS.HG00512_010101_AAABBB11XX_1.fastq.gz', 'CHS.HG00512_010101_AAABBB11XX_2.fastq.gz']) ==  sorted([x.basename for x in samples.join("CHS").listdir()])
    elif name == "sample_run":
        assert sorted(samples_ind) == sorted([x.basename for x in samples.listdir()])
    elif name == "sample_project_run":
        fqfiles = [str(p.basename) for p in samples.visit() if p.isfile()]
        assert 'PUR.HG00731_010101_AAABBB11XX_2.fastq.gz' in fqfiles
        assert 'PUR.HG00733_020202_AAABBB22XX_2.fastq.gz' in fqfiles
        assert sorted(["p1", "p2"]) == sorted([x.basename for x in samples.join("PUR.HG00731").listdir()])
    elif name == "pop_sample":
        assert "PUR_010101_AAABBB11XX_1.fastq.gz" in [x.basename for x in samples.join("PUR").join("PUR").listdir()]
    elif name == "pop_sample_run":
        assert 6 == len([str(p) for p in samples.visit() if p.isfile()])
    elif name == "pop_sample_project_run":
        assert 6 == len([str(p) for p in samples.visit() if p.isfile()])


@pytest.mark.ref(copy=False)
@pytest.mark.parametrize("testdir,copy",[(("foo"), (False)), (("bar"), (True))])
def test_layouts_request(samples, ref, testdir, copy):
    assert str(samples).endswith("{}/data".format(testdir))
    assert str(ref).endswith("{}/ref".format(testdir))
    if testdir == "foo":
        assert samples.join("s1_1.fastq.gz").islink()
    elif testdir == "bar":
        assert samples.join("s1_1.fastq.gz").isfile()
