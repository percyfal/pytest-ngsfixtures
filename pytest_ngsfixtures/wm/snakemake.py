#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import inspect
import pytest
import py
import logging
from pytest_ngsfixtures.os import safe_mktemp, safe_copy, safe_symlink
from pytest_ngsfixtures.shell import shell
from pytest_ngsfixtures.wm.utils import save_command


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def snakefile(request, tmpdir_factory):
    """Return a temporary directory path object pointing to the location
    of a Snakefile.

    If no snakefile is defined with pytest.mark.snakefile, the fixture
    will assume there is a Snakefile in the same directory as the
    calling test file.

    Examples:

      .. code-block:: python

         @pytest.mark.snakefile(snakefile="/path/to/Snakefile", dirname="foo")
         def test_snakefile(snakefile):
             print(snakefile.listdir())

    """
    options = {
        'dirname': '',
        'copy': True,
        'snakefile': py.path.local(request.fspath.dirname).join("Snakefile"),
        'numbered': False,

    }
    if 'snakefile' in request.keywords:
        options.update(request.keywords.get('snakefile').kwargs)
    p = safe_mktemp(tmpdir_factory, **options)
    src = options['snakefile']
    f = safe_copy if options['copy'] else safe_symlink
    dst = f(p, src)
    return dst


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
