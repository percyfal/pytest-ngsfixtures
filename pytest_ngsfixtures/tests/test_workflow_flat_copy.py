# -*- coding: utf-8 -*-
import pytest
from pytest_ngsfixtures.wm.snakemake import snakefile, run as snakemake_run


@pytest.mark.samples(numbered=True)
@pytest.mark.snakefile(dirname="snakefile", numbered=True)
def test_workflow(snakefile, samples):
    snakemake_run(snakefile, options=["-d", str(samples), "-s",
                                      str(snakefile)])
    assert samples.join("results.txt").exists()
