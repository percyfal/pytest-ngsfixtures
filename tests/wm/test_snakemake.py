#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import py
import pytest
from pytest_ngsfixtures.wm import snakemake


Snakefile = snakemake.snakefile_factory(
    copy=True, numbered=True)


def test_local_wf(Snakefile):
    snakemake.run(Snakefile, options=["-d", str(Snakefile.dirname)])
    files = [x.basename for x in py.path.local(Snakefile.dirname).listdir()]
    assert "foo.txt" in files


@pytest.mark.snakemake
def test_container_wf(Snakefile, snakemake_container):
    snakemake_container.start()
    snakemake.run(Snakefile.basename, container=snakemake_container, bash=True,
                  working_dir=Snakefile.dirname)
    files = [x.basename for x in py.path.local(Snakefile.dirname).listdir()]
    assert "foo.txt" in files


@pytest.mark.snakemake
def test_image_wf(Snakefile, snakemake_image, image_args):
    snakemake.run(Snakefile, options=["-d", str(Snakefile.dirname)],
                  image=snakemake_image, bash=True,
                  working_dir=Snakefile.dirname, **image_args)
    files = [x.basename for x in py.path.local(Snakefile.dirname).listdir()]
    assert "foo.txt" in files
