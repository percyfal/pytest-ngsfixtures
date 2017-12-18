# -*- coding: utf-8 -*-
from pytest_ngsfixtures.wm import snakemake
from pytest_ngsfixtures import factories

flatc = factories.sample_layout(sample=["CHS.HG00512"],
                                dirname="flat_copy",
                                numbered=True, copy=True)

Snakefile = snakemake.snakefile_factory(
    copy=True, numbered=True)


def test_workflow(Snakefile, flatc):
    snakemake.run(Snakefile, options=["-d", str(flatc), "-s",
                                      str(Snakefile)])
    assert flatc.join("results.txt").exists()
