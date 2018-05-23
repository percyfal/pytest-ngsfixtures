#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import py
import pytest
from pytest_ngsfixtures.wm.snakemake import snakefile, run as snakemake_run


@pytest.mark.snakefile(numbered=True)
def test_local_wf(snakefile):
    snakemake_run(snakefile)
    files = [x.basename for x in py.path.local(snakefile.dirname).listdir()]
    assert "foo.txt" in files


@pytest.mark.snakefile(numbered=True)
@pytest.mark.snakemake
def test_container_wf(snakefile, snakemake_container):
    snakemake_container.start()
    snakemake_run(snakefile, container=snakemake_container)
    files = [x.basename for x in py.path.local(snakefile.dirname).listdir()]
    assert "foo.txt" in files


@pytest.mark.snakefile(numbered=True)
@pytest.mark.snakemake
def test_image_wf(snakefile, snakemake_image, image_args):
    snakemake_run(snakefile, image=snakemake_image,
                  **image_args)
    files = [x.basename for x in py.path.local(snakefile.dirname).listdir()]
    assert "foo.txt" in files
