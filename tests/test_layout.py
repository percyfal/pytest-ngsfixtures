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
from pytest_ngsfixtures.layout import generate_sample_layouts, setup_sample_layout, setup_reference_layout


def test_generate_sample_layouts():
    layout = generate_sample_layouts()
    samples = [x['sample'] for x in layout]
    assert set(['PUR.HG00731.A', 'PUR.HG00731.B', 'PUR.HG00733.A']) == set(samples)
    assert len(layout) == 3


def test_filefixtures_from_sample_layouts(tmpdir):
    layout = generate_sample_layouts()
    for l in layout:
        r1 = ReadFixtureFile(runfmt="{SM}_{PU}", path=tmpdir, **l)
        r1.setup()
        r2 = ReadFixtureFile(runfmt="{SM}_{PU}", path=tmpdir, read=2,
                             copy=True, **l)
        r2.setup()
        assert r1.islink()
        assert r1.src.exists()
        assert not r2.islink()
        assert r2.computehash() == r2.src.computehash()
        assert r2.src.exists()


def test_setup_sample_layout_flat(tmpdir):
    p = setup_sample_layout(tmpdir, layout="short", runfmt="{SM}_{PU}")
    flist = [str(x.basename) for x in p.visit() if str(x).endswith(".fastq.gz")]
    assert 's1_010101_AAABBB11XX_2.fastq.gz' in flist


def test_setup_sample_layout_flat_sample(tmpdir):
    with pytest.raises(py.error.EEXIST):
        setup_sample_layout(tmpdir, layout="short", runfmt="{SM}")


def test_setup_sample_layout_flat_sample_copy(tmpdir):
    with pytest.raises(py.error.EEXIST):
        setup_sample_layout(tmpdir, layout="short", runfmt="{SM}", copy=True)


def test_setup_sample_layout_individual(tmpdir):
    p = setup_sample_layout(tmpdir, layout="individual", sampleinfo=True)
    flist = [x.basename for x in p.visit() if str(x).endswith(".fastq.gz")]
    assert "PUR.HG00731_010101_AAABBB11XX_1.fastq.gz" in flist
    assert "PUR.HG00731_020202_AAABBB22XX_1.fastq.gz" in flist
    header = p.join("sampleinfo.csv").readlines()[0].strip()
    assert header == "PU,SM,fastq"


def test_setup_reference_layout(tmpdir_factory):
    path = safe_mktemp(tmpdir_factory, dirname="ref", numbered=True)
    path = setup_reference_layout(path)
    flist = [x.basename for x in path.visit()]
    assert "ref.fa" in flist
    assert "scaffolds.fa" not in flist


@pytest.fixture(scope="function", autouse=False)
def reference_data(tmpdir_factory):
    path = safe_mktemp(tmpdir_factory, dirname="ref", numbered=True)
    path = setup_reference_layout(path, label="ref")
    return path


def test_reference_data(reference_data):
    print(reference_data)
    print(reference_data.listdir())


def test_setup_sample_layout_individual_pop(tmpdir):
    path = setup_sample_layout(tmpdir, layout="individual",
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
