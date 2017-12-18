# -*- coding: utf-8 -*-
from pytest_ngsfixtures.wm import snakemake

Snakefile = snakemake.snakefile_factory(
    copy=True, numbered=True)


def test_workflow(Snakefile, flat):
    snakemake.run(Snakefile, options=["-d", str(flat)])
    assert flat.join("results.txt").exists()
