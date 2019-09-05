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


def pytest_configure(config):
    regex = re.compile(SNAKEMAKE_VERSION)
    if config.cache.get("pytest_ngsfixtures/tags", None) is None:
        try:
            import requests
            r = requests.get(
                "https://quay.io/api/v1/repository/biocontainers/snakemake/tag")
            tags = sorted([t['name'] for t in r.json()['tags']], reverse=True)
            config.cache.set("pytest_ngsfixtures/tags", tags)
        except Exception:
            logger.error("couldn't complete requests for quay.io")
            raise
    for t in sorted(config.cache.get("pytest_ngsfixtures/tags", []), reverse=True):
        if regex.search(t):
            snakemake_tag = t
            break

    pytest.snakemake_repo = "{repo}:{tag}".format(
        repo=SNAKEMAKE_REPO,
        tag=snakemake_tag)
