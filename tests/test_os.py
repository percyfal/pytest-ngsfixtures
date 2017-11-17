# -*- coding: utf-8 -*-
"""
test_pytest_os
----------------------------------

Tests for `pytest_ngsfixtures.os` module.
"""
import os
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


def test_safe_symlink(tmpdir_factory, bam):
    print(str(bam))
    p = tmpdir_factory.mktemp("safe_symlink")
    # Test using string as input without capturing return
    safe_symlink(p, str(bam), "bar/foo.bar")
    assert str(p).endswith("safe_symlink0")
    # Test using string as input
    l = safe_symlink(p, str(bam), "foo/foo.bar")
    assert str(l).endswith("foo/foo.bar")
    assert l.realpath() == bam.realpath()
    # Test using localpath as input
    l = safe_symlink(p, bam, "foo.bar")
    assert l.realpath() == bam.realpath()
    assert str(l).endswith("foo.bar")


def test_safe_copy(tmpdir_factory, bam):
    p = tmpdir_factory.mktemp("safe_copy")
    safe_copy(p, bam, "bar/foo.bar")
    assert str(p).endswith("safe_copy0")
    # Test using string as input
    c = safe_copy(p, str(bam), "foo/foo.bar")
    assert str(c).endswith("foo/foo.bar")
    assert c.realpath() != bam.realpath()
    # Test using localpath as input
    c = safe_copy(p, bam, "foo.bar")
    assert c.realpath() != bam.realpath()
    assert str(c).endswith("foo.bar")
    # Test that file is *not* a symlink and that it is equal to target
    # fixture
    assert c.size() == bam.size()
    assert c.computehash() == bam.computehash()
