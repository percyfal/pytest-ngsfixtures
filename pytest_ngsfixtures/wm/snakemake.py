#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
import py
import logging
from pytest_ngsfixtures.os import safe_mktemp
from pytest_ngsfixtures.file import setup_filetype
from pytest_ngsfixtures.shell import shell


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def snakefile_factory(snakefile, **kwargs):
    """
    Fixture factory for snakefile.

    Example:

      .. code-block:: python

         from pytest_ngsfixtures.wm import snakemake
         snakefile = snakemake.snakefile_factory("/path/to/Snakfile")

         def test_workflow(snakefile, flat):
             snakemake.run(target=flat.join())

    Args:
      snakefile (str, py._path.local.LocalPath): snakefile path

    """
    @pytest.fixture(scope=kwargs.get("scope", "function"),
                    autouse=kwargs.get("autouse", False))
    def snakefile_fixture(request, tmpdir_factory):
        """Snakefile fixture"""
        sf = snakefile
        if isinstance(sf, str):
            sf = py.path.local(sf)
        assert isinstance(sf, py._path.local.LocalPath)
        assert sf.exists()
        p = safe_mktemp(tmpdir_factory, "snakefile", **kwargs)
        p = p.join("Snakefile")
        p = setup_filetype(path=p, src=sf, **kwargs)
        if request.config.option.ngs_show_fixture:
            logger.info("-------------------------")
            logger.info("Snakefile fixture content")
            logger.info("-------------------------")
            logger.info(str(p))
        return p
    return snakefile_fixture


def run(Snakefile, target="all", options=[], bash=False,
        working_dir=None, **kwargs):
    cmd_args = ["snakemake", "-s", str(Snakefile), target] + options

    if working_dir:
        cmd_args = ["cd", working_dir, "&&"] + cmd_args
    cmd = " ".join(cmd_args)
    if bash:
        cmd = "/bin/bash -c '{}'".format(cmd)
    logger.info(cmd)
    shell(cmd, **kwargs)
