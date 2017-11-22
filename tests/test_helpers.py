#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_helpers
----------------------------------

Tests for `pytest_ngsfixtures.helpers` module.
"""
import pytest
from pytest_ngsfixtures import helpers, config


@pytest.fixture
def subconfig():
    conf = {'samtools': config.application_config()['samtools']}
    return conf


class MockRule(object):
    def __init__(self, name, output):
        self._name = name
        self._output = output

    @property
    def name(self):
        return self._name

    @property
    def output(self):
        return self._output


def test_make_targets(subconfig):
    rules = [MockRule(name="samtools_depth", output={"txt": "{version}/{end}/medium.depth.txt"}),
             MockRule(name="samtools_rmdup", output={"txt": "{version}/{end}/medium.rmdup.txt"})]
    tgt = helpers.make_targets(rules, subconfig, 'samtools', end='se')
    assert len(tgt) == 8


def test_get_versions(subconfig):
    conf = subconfig['samtools']
    all_versions = helpers.get_versions(conf)
    samtools_stats_versions = helpers.get_versions(conf['samtools_stats'], all_versions)
    samtools_rmdup_versions = helpers.get_versions(conf['samtools_rmdup'], all_versions)
    assert all_versions == set(conf["_versions"]).intersection(set(conf["_conda_versions"]))
    assert samtools_stats_versions == all_versions
    assert samtools_rmdup_versions != all_versions


def test_make_stats_targets(subconfig):
    rules = [
        MockRule(name="samtools_rmdup", output={"txt": "{version}/{end}/medium.rmdup.txt"}),
        MockRule(name="samtools_stats", output={"txt": "{version}/{end}/medium.stats.txt"}),
    ]
    tgt = helpers.make_targets(rules, subconfig, 'samtools', end='se')
    assert "1.5/se/medium.stats.txt" in tgt
    tgt = helpers.make_targets(rules, subconfig, 'samtools', end='pe')
    assert "1.5/pe/medium.stats.txt" in tgt
