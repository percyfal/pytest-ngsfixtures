# -*- coding: utf-8 -*-
import os

__author__ = """Per Unneberg"""
__email__ = 'per.unneberg@scilifelab.se'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
