#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_config
----------------------------------

Tests for `pytest_ngsfixtures.config` module.
"""
import os
import pytest
from pytest_ngsfixtures import config


def test_collect_config():
    conf = config.application_config()
    assert 'bwa' in conf.keys()
    assert 'fastqc' in conf.keys()
    assert 'input' in conf.keys()


def test_collect_bwa_config_application():
    conf = config.application_config('bwa')
    assert 'bwa' in conf.keys()
    assert 'fastqc' not in conf.keys()
    assert 'input' in conf.keys()


def test_collect_samtools_config_application():
    conf = config.application_config('samtools')
    assert 'samtools' in conf.keys()
    assert 'fastqc' not in conf.keys()
    assert 'input' in conf.keys()


def test_get_bwa_application_fixture():
    af = config.get_application_fixture('bwa', 'bwa_mem', '0.5.9', 'se')
    assert af['log'] == 'bwa/0.5.9/se/bwa_mem.log'


# Special in that no se/pe exists
def test_get_samtools_faidx_application_fixture():
    af = config.get_application_fixture('samtools', 'samtools_faidx', '1.3.1')
    assert af['fai'] == 'samtools/1.3.1/scaffoldsN.fa.fai'


def test_get_nonexisting_application_fixture():
    with pytest.raises(KeyError):
        config.get_application_fixture('foo', 'bar', '1.0.0')


def test_get_every_application_fixture():
    conf = config.application_config()
    for ad in config.APPLICATION_DIRECTORIES:
        app = os.path.basename(ad)
        version = conf[app]['_default']
        for command in conf[app].keys():
            if command.startswith("_"):
                continue
            af = config.get_application_fixture(app, command, version, 'se')
            for x in af.values():
                assert os.path.dirname(x).startswith(os.path.join(app, str(version)))


def test_output_list():
    conf = config.application_config()
    print(conf)
