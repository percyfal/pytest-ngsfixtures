# -*- coding: utf-8 -*-
import os
import pytest
from pytest_ngsfixtures import DATA_DIR, factories
from pytest_ngsfixtures.os import localpath
from pytest_ngsfixtures.fixtures import *

pytest_plugins = 'pytester'


@pytest.fixture(scope="module", autouse=False)
def tiny_fastq_files():
    """Fixture that returns list of all tiny fastq files"""
    for path, dirs, files in os.walk(os.path.join(DATA_DIR, "tiny")):
        filelist = sorted([os.path.join(DATA_DIR, "tiny", x) for x in files])
    return filelist


# Local files
PURHG00731 = localpath(os.path.join("applications", "pe",
                                    "PUR.HG00731.tiny.bam"))
PURHG00733 = localpath(os.path.join("applications", "pe",
                                    "PUR.HG00733.tiny.bam"))


# File fixtures
@pytest.fixture(scope="function", autouse=False)
def bamfile():
    """Bamfile fixture"""
    return PURHG00731


bam = factories.filetype(PURHG00731.basename,
                         fdir="bamfoo", scope="function",
                         numbered=True)
bam_copy = factories.filetype(PURHG00731.basename, fdir="bamfoo",
                              scope="function", numbered=True,
                              copy=True)
renamebam = factories.filetype(PURHG00731.basename,
                               fdir="renamebamfoo", scope="function",
                               numbered=True, alias="s.tiny.bam")
renamebam_copy = factories.filetype(PURHG00731.basename, fdir="renamebamfoo",
                                    scope="function", numbered=True,
                                    alias="s.tiny.bam", copy=True)


# Multifile fixtures
_PURFILES = [PURHG00731.relto(DATA_DIR), PURHG00733.relto(DATA_DIR)]


@pytest.fixture(scope="function", autouse=False)
def PURFILES():
    """List of bam files"""
    return [PURHG00731, PURHG00733]


bamset = factories.fileset(src=_PURFILES, fdir="bamset",
                           scope="function")

_dstfiles = ["foo.fastq.gz", "bar.fastq.gz"]


@pytest.fixture(scope="function", autouse=False)
def dstfiles():
    """Destination file names"""
    return _dstfiles


bamset2 = factories.fileset(src=_PURFILES, dst=_dstfiles,
                            fdir="bamset2", scope="function")
