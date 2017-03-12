#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `pytest_ngsfixtures.config` module.
"""
import os
import re
import pytest
from pytest_ngsfixtures import config
import yaml


def test_collect_config():
    """Test collection of config in application directories works"""
    conf = config.application_config()
    assert 'bwa' in conf.keys()
    assert 'fastqc' in conf.keys()
    assert 'input' in conf.keys()


def test_collect_config_application():
    """Test collection of one application configuration"""
    conf = config.application_config('bwa')
    assert 'bwa' in conf.keys()
    assert 'fastqc' not in conf.keys()
    assert 'input' in conf.keys()


def test_output_list():
    conf = config.application_config()
    print(conf)
