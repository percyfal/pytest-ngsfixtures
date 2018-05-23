# -*- coding: utf-8 -*-
import pytest
from pytest_ngsfixtures.wm.snakemake import snakefile, run as snakemake_run


@pytest.mark.samples(copy=False, numbered=True)
@pytest.mark.snakefile(copy=False, dirname="snakefile", numbered=True)
def test_workflow(samples, snakefile):
    snakemake_run(snakefile, options=["-d", str(samples)])
    assert samples.join("results.txt").exists()
