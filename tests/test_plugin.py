#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from pytest_ngsfixtures.plugin import Fixture


@pytest.mark.testdata(dirname="foo")
def test_fixture_testdata(testdata):
    assert str(testdata).endswith("foo")


@pytest.mark.testdata(dirname="foo", testunit="bar")
def test_fixture_testdata_testunit(testdata):
    assert str(testdata).endswith("bar/foo")
    

def test_fixture_testdata_class():
    p = Fixture(dirname="foo")
    assert str(p).endswith("foo")


def test_fixture_testdata_testunit_class():
    p = Fixture(dirname="foo", testunit="bar")
    assert str(p).endswith("bar/foo")
    
