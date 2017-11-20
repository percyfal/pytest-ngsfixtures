# -*- coding: utf-8 -*-
import os
import py
import pytest
from pytest_ngsfixtures.file import FixtureFile, ReadFixtureFile


@pytest.fixture
def foo(tmpdir):
    p = tmpdir.join("foo.txt")
    p.write("foo")
    return p


def test_init(foo):
    f = FixtureFile(foo, src=foo)
    assert f.src.dirname == foo.dirname


def test_init_w_str():
    f = FixtureFile("foo.txt")
    assert f.path.isdir()


def test_init_wo_path():
    f = FixtureFile()
    assert f.isdir()


def test_read():
    r = ReadFixtureFile("CHS.HG00512")
    assert str(r.path) == os.path.abspath(os.curdir)


def test_setup_read_link(tmpdir):
    p = tmpdir.mkdir("setup")
    r = ReadFixtureFile("CHS.HG00512", path=p)
    r.setup()
    assert r.samefile(r.src)
    assert r.islink()


def test_setup_read_copy(tmpdir):
    p = tmpdir.mkdir("setup")
    r = ReadFixtureFile("CHS.HG00512", path=p, copy=True)
    r.setup()
    assert r.computehash() == r.src.computehash()
    assert not r.islink()


def test_read_dict(foo):
    h = ReadFixtureFile("CHS.HG00512")
    assert sorted(list(dict(h).keys())) == ['BATCH', 'POP', 'PU', 'SM']


def test_read_fmt():
    r = ReadFixtureFile("CHS.HG00512")
    print(str(r))
    
