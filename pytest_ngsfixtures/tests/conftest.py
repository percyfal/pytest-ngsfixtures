#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import subprocess as sp
import logging
import pytest

logger = logging.getLogger(__name__)

PYTHON_VERSION = "py{}{}".format(sys.version_info.major,
                                 sys.version_info.minor)
try:
    SNAKEMAKE_VERSION = sp.check_output(
        ["snakemake", "--version"]).decode().strip()
except Exception:
    logger.error("couldn't get snakemake version")
    raise

SNAKEMAKE_REPO = "quay.io/biocontainers/snakemake"
SNAKEMAKE_IMAGE = "{}:{}".format(SNAKEMAKE_REPO, SNAKEMAKE_VERSION)


def get_snakemake_quay_tag():
    import requests
    try:
        r = requests.get(
            "https://quay.io/api/v1/repository/biocontainers/snakemake/tag")
        tags = [t['name'] for t in r.json()['tags']]
    except Exception:
        logger.error("couldn't complete requests for quay.io")
        raise
    r = re.compile(SNAKEMAKE_VERSION)
    for t in sorted(tags, reverse=True):
        if r.search(t):
            return t
    logger.error("No valid snakemake tag found")
    sys.exit(1)


def pytest_configure(config):
    pytest.snakemake_repo = "{repo}:{tag}".format(
        repo=SNAKEMAKE_REPO,
        tag=get_snakemake_quay_tag())
