# -*- coding: utf-8 -*-

"""
test_layout
----------------------------------

Tests for `pytest_ngsfixtures.layout` module.
"""
import pytest
import py
from pytest_ngsfixtures.os import safe_mktemp
from pytest_ngsfixtures.file import ReadFixtureFile
from pytest_ngsfixtures.layout import generate_sample_layouts, sample_fixture_layout, reference_fixture_layout


def test_generate_sample_layouts():
    layout = generate_sample_layouts()
    samples = [x['sample'] for x in layout]
    assert set(['PUR.HG00731.A', 'PUR.HG00731.B', 'PUR.HG00733.A']) == set(samples)
    assert len(layout) == 3


def test_filefixtures_from_sample_layouts(tmpdir):
    layout = generate_sample_layouts()
    p = tmpdir.mkdir("layout")
    for l in layout:
        r1 = ReadFixtureFile(runfmt="{SM}_{PU}", path=p, **l)
        r1.setup()
        r2 = ReadFixtureFile(runfmt="{SM}_{PU}", path=p, read=2,
                             copy=True, **l)
        r2.setup()
        assert r1.islink()
        assert r1.src.exists()
        assert not r2.islink()
        assert r2.computehash() == r2.src.computehash()
        assert r2.src.exists()


def test_sample_fixture_layout_flat(tmpdir_factory):
    p = safe_mktemp(tmpdir_factory)
    p = sample_fixture_layout(p)
    flist = [str(x.basename) for x in p.visit() if str(x).endswith(".fastq.gz")]
    assert 's1_010101_AAABBB11XX_2.fastq.gz' in flist


def test_sample_fixture_layout_flat_sample(tmpdir_factory):
    p = safe_mktemp(tmpdir_factory)
    with pytest.raises(py.error.EEXIST):
        sample_fixture_layout(p, runfmt="{SM}")


def test_sample_fixture_layout_flat_sample_copy(tmpdir_factory):
    p = safe_mktemp(tmpdir_factory)
    with pytest.raises(py.error.EEXIST):
        sample_fixture_layout(p, runfmt="{SM}", copy=True)


def test_sample_fixture_layout_individual(tmpdir_factory):
    p = safe_mktemp(tmpdir_factory)
    p = sample_fixture_layout(p, layout="individual", sampleinfo=True)
    flist = [x.basename for x in p.visit() if str(x).endswith(".fastq.gz")]
    assert "PUR.HG00731_010101_AAABBB11XX_1.fastq.gz" in flist
    assert "PUR.HG00731_020202_AAABBB22XX_1.fastq.gz" in flist
    header = p.join("sampleinfo.csv").readlines()[0].strip()
    assert header == "PU,SM,fastq"


def test_reference_fixture_layout(tmpdir):
    path = reference_fixture_layout(tmpdir.join("ref"))
    flist = [x.basename for x in path.visit()]
    assert "ref.fa" in flist
    assert "scaffolds.fa" not in flist


def test_sample_fixture_layout_individual_pop(tmpdir):
    path = sample_fixture_layout(tmpdir, layout="individual",
                                 sampleinfo=True, runfmt="{POP}/{BATCH}/{PU}/{SM}")
    flist = [x.basename for x in path.visit() if str(x).endswith(".fastq.gz")]
    assert "PUR.HG00731_1.fastq.gz" in flist
    assert "PUR.HG00731_1.fastq.gz" in flist
    sampleinfo = sorted(path.join("sampleinfo.csv").readlines())
    header = sampleinfo[0].strip()
    assert header == "BATCH,POP,PU,SM,fastq"
    chs = sampleinfo[2].strip().split(",")
    assert chs[0] == "p1"
    assert chs[1] == "CHS"
    assert chs[4] == "CHS/p1/010101_AAABBB11XX/CHS.HG00512_2.fastq.gz"
