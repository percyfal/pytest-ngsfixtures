# -*- coding: utf-8 -*-
import os
import pathlib
from ._version import get_versions

__author__ = """Per Unneberg"""
__email__ = 'per.unneberg@scilifelab.se'
__version__ = get_versions()['version']
del get_versions

# Package root and data directory paths
ROOT_DIR = pathlib.Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
