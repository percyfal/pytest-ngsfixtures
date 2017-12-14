#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pytest
from pytest_ngsfixtures.wm import snakemake

print(type(pytest.rootdir))
print(pytest.rootdir)
snakefile1 = snakemake.snakefile_factory(
    pytest.rootdir.join(os.path.join("wm", "examples", "Snakefile")), copy=True)


def test_wf1(snakefile1):
    print(snakefile1.readlines())
