# -*- coding: utf-8 -*-
import os
import pytest
from pytest_ngsfixtures.file import FixtureFile, ReadFixtureFile, ReferenceFixtureFile, ApplicationOutputFixture, fixturefile_factory


@pytest.fixture
def foo(tmpdir):
    p = tmpdir.join("foo.txt")
    p.write("foo")
    return p


def test_init(foo):
    f = FixtureFile(foo, src=foo)
    assert f.src.dirname == foo.dirname


def test_init_w_str(tmpdir, foo):
    f = FixtureFile("foo.txt", src=foo)
    assert f.path.isdir()


def test_init_wo_path(foo):
    f = FixtureFile(src=foo)
    assert f.isdir()


def test_read():
    r = ReadFixtureFile("CHS.HG00512")
    assert str(r.path) == os.path.abspath(os.curdir)


def test_setup_read_link(tmpdir):
    r = ReadFixtureFile("CHS.HG00512", path=tmpdir)
    r.setup()
    assert r.samefile(r.src)
    assert r.islink()


def test_setup_read_copy(tmpdir):
    r = ReadFixtureFile("CHS.HG00512", path=tmpdir, copy=True)
    r.setup()
    assert r.computehash() == r.src.computehash()
    assert not r.islink()


def test_read_dict(foo):
    h = ReadFixtureFile("CHS.HG00512")
    assert sorted(list(dict(h).keys())) == ['BATCH', 'POP', 'PU', 'SM']


def test_read_fmt(tmpdir):
    r = ReadFixtureFile("CHS.HG00512", path=tmpdir)
    assert r.basename == "CHS.HG00512_1.fastq.gz"
    r = ReadFixtureFile("CHS.HG00512", runfmt="{POP}/{PU}/{SM}_{PU}", path=tmpdir)
    assert r.dirname.endswith("CHS/010101_AAABBB11XX")


def test_read_sampleinfo(tmpdir):
    r = ReadFixtureFile("CHS.HG00512", path=tmpdir,
                        runfmt="{POP}/{PU}/{SM}_{PU}",
                        sampleinfo=True)
    assert r.sampleinfo == "CHS,010101_AAABBB11XX,CHS.HG00512,CHS/010101_AAABBB11XX/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz"


def test_read_sampleinfo_alias(tmpdir):
    r = ReadFixtureFile("PUR.HG00733.A", path=tmpdir,
                        runfmt="{POP}/{PU}/{SM}_{PU}",
                        alias="PUR.HG00733",
                        platform_unit="010101_AAABBB11XX",
                        sampleinfo=True)
    assert r.sampleinfo == "PUR,010101_AAABBB11XX,PUR.HG00733,PUR/010101_AAABBB11XX/PUR.HG00733_010101_AAABBB11XX_1.fastq.gz"


def test_read_alias(tmpdir):
    r = ReadFixtureFile("CHS.HG00512", path=tmpdir, alias="s",
                        platform_unit="foo_bar", runfmt="{SM}_{PU}",
                        read=2)
    assert r.basename == "s_foo_bar_2.fastq.gz"


def test_populations(tmpdir):
    chs = ReadFixtureFile("CHS")
    pur = ReadFixtureFile("PUR")
    yri = ReadFixtureFile("YRI")
    assert chs.basename == "CHS_1.fastq.gz"
    assert pur.basename == "PUR_1.fastq.gz"
    assert yri.basename == "YRI_1.fastq.gz"
    hg00731 = ReadFixtureFile("PUR.HG00731",
                              path=tmpdir.join("s1.fastq.gz"),
                              runfmt="{SM}_{PU}", setup=True)
    hg00731a = ReadFixtureFile("PUR.HG00731.A",
                               path=tmpdir.join("s2.fastq.gz"),
                               runfmt="{SM}_{PU}", setup=True)
    assert hg00731.islink()
    if "TRAVIS" not in os.environ:
        assert hg00731.src.realpath().basename == "PUR.HG00731.A_1.fastq.gz"
        assert hg00731.src.realpath() == hg00731a.src
        assert hg00731.src != hg00731.src.realpath()


def test_ref(tmpdir):
    r = ReferenceFixtureFile("ref.fa")
    assert r.dirname == os.path.abspath(os.curdir)
    r = ReferenceFixtureFile(tmpdir.join("ref.fa"))
    assert r.dirname == tmpdir


def test_wrong_ref():
    with pytest.raises(AssertionError):
        ReferenceFixtureFile("foo.fa")


def test_census():
    ReadFixtureFile.reset()
    ReadFixtureFile()
    r2 = ReadFixtureFile()
    assert r2.census == 2


def test_short_name():
    ReadFixtureFile.reset()
    r1 = ReadFixtureFile(short_name=True)
    assert r1.basename == "s1_1.fastq.gz"
    r2 = ReadFixtureFile(short_name=False)
    assert r2.basename == "CHS.HG00512_1.fastq.gz"
    r3 = ReadFixtureFile(short_name=True)
    assert r3.basename == "s3_1.fastq.gz"


def test_chrom_sizes(tmpdir):
    flist = ReferenceFixtureFile().ref['ref']
    src = flist[[x.basename for x in flist].index("ref.chrom.sizes")]
    ref = ReferenceFixtureFile(tmpdir.join("chrom.sizes"), src=src)
    ref.setup()
    assert ref.samefile(src)


def test_fixturefile_factory_raises():
    with pytest.raises(AssertionError):
        fixturefile_factory()
    with pytest.raises(AssertionError):
        fixturefile_factory(path="foo.bar")


def test_fixturefile_factory(tmpdir):
    ff = fixturefile_factory(tmpdir, application="samtools", command="samtools_flagstat", version="1.5", setup=True)
    assert type(ff) == ApplicationOutputFixture
    ff = fixturefile_factory(tmpdir, application="qualimap", command="qualimap_bamqc_pe", version="2.2.2a", setup=True, full=False)
    assert type(ff) == ApplicationOutputFixture
    ff = fixturefile_factory(tmpdir.join("ref.fa"), setup=True)
    assert type(ff) == ReferenceFixtureFile
    assert tmpdir.join("samtools").exists()
    assert tmpdir.join("samtools").isdir()
    assert not tmpdir.join("qualimap").exists()
