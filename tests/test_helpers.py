#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_helpers
----------------------------------

Tests for `pytest_ngsfixtures.helpers` module.
"""
from pytest_ngsfixtures import helpers, config


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


def test_make_targets():
    rules = [MockRule(name="samtools_depth", output={"txt": "{version}/{end}/medium.depth.txt"}),
             MockRule(name="samtools_rmdup", output={"txt": "{version}/{end}/medium.rmdup.txt"})]
    conf = config.application_config()
    tgt = helpers.make_targets(rules, conf, 'samtools', end='se')
    assert len(tgt) == 8
