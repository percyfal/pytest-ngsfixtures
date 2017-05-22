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


def test_application_fixtures():
    fixtures = config.application_fixtures(application="picard", version="2.9.0", end="pe")
    f = [fixt for fixt in fixtures if fixt[1] == "picard_CollectRrbsMetrics"][0]
    module, command, version, end, fmtdict = f
    assert isinstance(fmtdict, dict)
    assert len(fmtdict.keys()) == 2
    assert sorted(fmtdict.keys()) == sorted(['summary', 'detail'])


def test_application_fixtures_oneend():
    fixtures = config.application_fixtures(application="picard", version="2.9.0", end="pe")
    f = [fixt for fixt in fixtures if fixt[1] == "picard_CollectInsertSizeMetrics"]
    assert len(f) == 1
    fixtures = config.application_fixtures(application="picard", version="2.9.0", end="se")
    # should not exist
    assert len([fixt for fixt in fixtures if fixt[1] == "picard_CollectInsertSizeMetrics"]) == 0


def test_all_application_fixtures_oneend():
    fixtures = config.application_fixtures()
    # Make sure CollectInsertSizeMetrics lacks se case
    flist = [fixt for fixt in fixtures if fixt[1] == "picard_CollectInsertSizeMetrics" and fixt[2] == "2.9.0"]
    assert len(flist) == 1


def test_application_fixtures_qualimap():
    """Make sure bamqc_se does not return insert size files"""
    fixtures = config.application_fixtures(application="qualimap")
    for x in fixtures:
        if x[3] == "pe":
            assert any("insert" in y for y in x[4].values())
        else:
            assert not any("insert" in y for y in x[4].values())
