# -*- coding: utf-8 -*-
import pytest
from pytest_ngsfixtures.config import layout
from pytest_ngsfixtures.wm.snakemake import snakefile, run as snakemake_run


def test_workflow(snakefile, samples):
    snakemake_run(snakefile, options=["-d", str(samples)])
    assert samples.join("results.txt").exists()
