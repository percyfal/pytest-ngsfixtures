# -*- coding: utf-8 -*-
import os
from ._version import get_versions

__author__ = """Per Unneberg"""
__email__ = 'per.unneberg@scilifelab.se'
__version__ = get_versions()['version']
del get_versions

# Package root and data directory paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.realpath(os.path.join(ROOT_DIR, "data"))
