# -*- coding: utf-8 -*-
from os.path import join, abspath, dirname
from pytest_ngsfixtures.wm import snakemake
from pytest_ngsfixtures import factories

flatc = factories.sample_layout(sample=["CHS.HG00512"],
                                copy=True)

Snakefile = snakemake.snakefile_factory(
    abspath(join(dirname(__file__), "Snakefile")),
    copy=True, numbered=True)


def test_workflow(Snakefile, flatc):
    snakemake.run(Snakefile, options=["-d", str(flatc), "-s",
                                      str(Snakefile)])
    assert flatc.join("results.txt").exists()
