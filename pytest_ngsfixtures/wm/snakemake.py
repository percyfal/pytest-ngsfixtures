#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import inspect
import pytest
import py
import logging
from pytest_ngsfixtures.os import safe_mktemp
from pytest_ngsfixtures.file import setup_filetype
from pytest_ngsfixtures.shell import shell
from pytest_ngsfixtures.wm.utils import save_command


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def snakefile_factory(snakefile=None, testdir=None, **kwargs):
    """Fixture factory for snakefile.

    If no snakefile is given, the factory will assume that there is a
    Snakefile in the same directory as the calling test file.

    Example:

      .. code-block:: python

         from pytest_ngsfixtures.wm import snakemake
         snakefile = snakemake.snakefile_factory("/path/to/Snakfile")

         def test_workflow(snakefile, flat):
             snakemake.run(snakefile)

         # Assumes there is a Snakefile in the test directory
         snakefile2 = snakemake.snakefile_factory()

         # Make specific target output.txt
         def test_workflow(snakefile2, flat):
             snakemake.run(snakefile2, target=flat.join("output.txt"))


    Args:
      snakefile (str, py._path.local.LocalPath): snakefile path
      testdir (str, py._path.local.LocalPath): output directory

    """
    if snakefile is None:
        s = inspect.stack()[1]
        snakefile = py.path.local(os.path.dirname(s.filename)).join("Snakefile")

    @pytest.fixture(scope=kwargs.get("scope", "function"),
                    autouse=kwargs.get("autouse", False))
    def snakefile_fixture(request, tmpdir_factory, pytestconfig):
        """Snakefile fixture"""
        sf = snakefile
        if isinstance(sf, str):
            sf = py.path.local(sf)
        assert isinstance(sf, py._path.local.LocalPath)
        assert sf.exists()
        p = testdir
        if p is None:
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


def run(snakefile, target="all",
        save=False, **kwargs):
    """Run snakemake on snakefile.

    Wraps snakefile in a command string and pass the string to shell
    wrapper.

    Examples:

      .. code-block:: python

         from pytest_ngsfixtures.wm import snakemake

         for r in snakemake.run("/path/to/Snakefile", target="test.bam",
                                options=["--ri -k"], iterable=True):
             print(r)

    Args:
      snakefile (str, py._path.local.LocalPath): snakefile full path name
      target (str): snakemake target to run
      options (list): options to pass to snakemake
      save (bool): save shell script with command

    Kwargs:
      See :py:mod:`pytest_ngsfixtures.shell.shell` documentation.

    Returns:
      Results from :py:mod:`~pytest_ngsfixtures.shell.shell`.

    """
    options = kwargs.pop("options", [])
    if not {"--directory", "-d"}.intersection(options):
        options += ["-d", py.path.local(snakefile).dirname]
    cmd_args = ["snakemake", "-s", str(snakefile), target] + options
    cmd = " ".join(cmd_args)
    if save:
        save_command(cmd, outfile=os.path.join(os.path.dirname(str(snakefile)), "command.sh"))
    return shell(cmd, **kwargs)
