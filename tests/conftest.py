# -*- coding: utf-8 -*-
import os
import pytest
from pytest_ngsfixtures import DATA_DIR

pytest_plugins = 'pytester'


@pytest.fixture(scope="module", autouse=False)
def tiny_fastq_files():
    """Fixture that returns list of all tiny fastq files"""
    for path, dirs, files in os.walk(os.path.join(DATA_DIR, "tiny")):
        filelist = sorted([os.path.join(DATA_DIR, "tiny", x) for x in files])
    return filelist
