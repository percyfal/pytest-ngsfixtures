# -*- coding: utf-8 -*-
"""Utilities for interacting with pytest-ngsfixtures repo.
"""
import os
import logging
from pytest_ngsfixtures import ROOT_DIR


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DOWNLOAD_SIZES = ["yuge"]
REPO = "https://raw.githubusercontent.com/percyfal/pytest-ngsfixtures/master"
PACKAGE_INSTALL_DIR = os.path.abspath(os.path.join(ROOT_DIR, os.pardir))


def download_sample_file(fn, size, dry_run=False, force=False):
    """Download sample file if it doesn't yet exist

    Setup urllib connection and download data file.

    Args:
      fn (str): file name as it appears in installed pytest_ngsfixtures data repository
      size (str): fixture file size
      dry_run (bool): don't do anything if set
      force (bool): force download

    Returns:
      url (str): url of target file if dry_run option passed, None otherwise

    """
    if size not in DOWNLOAD_SIZES:
        return
    if os.path.exists(fn) and not force:
        return
    else:
        import urllib.request
        import shutil
        url = os.path.join(REPO,
                           os.path.relpath(os.path.realpath(fn),
                                           os.path.realpath(PACKAGE_INSTALL_DIR)))
        if os.path.exists(fn):
            logger.info("File '{}' exists but force option passed; downloading file from git repo to local pytest_ngsfixtures installation location '{}'".format(fn, url))
        else:
            logger.info("File '{}' doesn't exist; downloading it from git repo to local pytest_ngsfixtures installation location '{}'".format(fn, url))
        if dry_run:
            return url
        try:
            if not os.path.exists(os.path.dirname(fn)):
                os.makedirs(os.path.dirname(fn))
            with urllib.request.urlopen(url) as response, open(fn, 'wb') as fh:
                shutil.copyfileobj(response, fh)
        except Exception as e:
            logger.error("Downloading '{}' failed: {}".format(url, e))
            raise


def _check_file_exists(fn, size):
    if size not in DOWNLOAD_SIZES:
        return
    if os.path.exists(fn):
        return
    else:
        logger.info("Sequence data in {} is not bundled with conda/PyPI packages to save space".format(size))
        logger.info("")
        logger.info("   Launch script 'pytest_ngsfixtures_download_data.py' to download missing files")
        logger.info("")
        raise FileNotFoundError
