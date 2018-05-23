# -*- coding: utf-8 -*-
"""
test_pytest_os
----------------------------------

Tests for `pytest_ngsfixtures.os` module.
"""
import os
import py
from pytest_ngsfixtures.os import safe_mktemp, safe_symlink, safe_copy


def test_safe_mktemp(tmpdir_factory):
    bn = tmpdir_factory.getbasetemp()
    p = safe_mktemp(tmpdir_factory)
    assert p == bn
    p = safe_mktemp(tmpdir_factory, dirname="foo")
    assert p == bn.join("foo")
    p = safe_mktemp(tmpdir_factory, dirname="foo", numbered=True)
    assert p == bn.join("foo0")
    p = safe_mktemp(tmpdir_factory, dirname=os.curdir)
    assert p == bn
    p = safe_mktemp(tmpdir_factory, dirname="foo/bar")
    assert p == bn.join("foo/bar")
    p = safe_mktemp(tmpdir_factory, dirname="foo/bar", numbered=True)
    assert p == bn.join("foo/bar0")


def test_safe_symlink(tmpdir_factory, readfile):
    p = tmpdir_factory.mktemp("safe_symlink")
    # Test using string as input without capturing return
    safe_symlink(p, str(readfile), "bar/foo.bar")
    assert str(p).endswith("safe_symlink0")
    # Test using string as input
    l = safe_symlink(p, str(readfile), "foo/foo.bar")
    assert str(l).endswith("foo/foo.bar")
    assert l.realpath() == str(readfile)
    # Test using localpath as input
    l = safe_symlink(p, readfile, "foo.bar")
    assert l.realpath() == str(readfile)
    assert str(l).endswith("foo.bar")


def test_safe_copy(tmpdir_factory, readfile):
    p = tmpdir_factory.mktemp("safe_copy")
    safe_copy(p, readfile, "bar/foo.bar")
    assert str(p).endswith("safe_copy0")
    # Test using string as input
    c = safe_copy(p, str(readfile), "foo/foo.bar")
    assert str(c).endswith("foo/foo.bar")
    assert c.realpath() != readfile.realpath()
    # Test using localpath as input
    c = safe_copy(p, readfile, "foo.bar")
    assert c.realpath() != readfile.realpath()
    assert str(c).endswith("foo.bar")
    # Test that file is *not* a symlink and that it is equal to target
    # fixture
    assert c.size() == readfile.size()
    assert c.computehash() == readfile.computehash()
