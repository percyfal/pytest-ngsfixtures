# -*- coding: utf-8 -*-
import os
import pytest
import subprocess as sp

Snakefile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         "examples", "Snakefile1"))


@pytest.fixture(scope="function", autouse=False)
def snakefile(flat):
    with open(Snakefile) as fh:
        lines = fh.readlines()
    with open(flat.join("Snakefile"), "w") as fh:
        fh.write("".join(lines))
    return flat


def test_workflow(snakefile):
    cmd_args = ["snakemake", "-d", snakefile, "-s",
                snakefile.join("Snakefile")]
    sp.check_output(cmd_args)
