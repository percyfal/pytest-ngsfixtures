# -*- coding: utf-8 -*-
import os
from ._version import get_versions

__author__ = """Per Unneberg"""
__email__ = 'per.unneberg@scilifelab.se'
__version__ = get_versions()['version']
del get_versions

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
