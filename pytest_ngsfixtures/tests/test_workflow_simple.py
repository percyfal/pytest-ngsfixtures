# -*- coding: utf-8 -*-
from os.path import join, abspath, dirname
from pytest_ngsfixtures.wm import snakemake

Snakefile = snakemake.snakefile_factory(
    snakefile=abspath(join(dirname(__file__), "Snakefile")),
    copy=True, numbered=True)


def test_workflow(Snakefile, flat):
    snakemake.run(Snakefile, options=["-d", str(flat)])
    assert flat.join("results.txt").exists()
