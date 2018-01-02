#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess as sp
import logging

logger = logging.getLogger(__name__)

PYTHON_VERSION = "py{}{}".format(sys.version_info.major,
                                 sys.version_info.minor)
try:
    SNAKEMAKE_VERSION = sp.check_output(
        ["snakemake", "--version"]).decode().strip()
except:
    logger.error("couldn't get snakemake version")
    raise

SNAKEMAKE_BASETAG = "{}--{}".format(SNAKEMAKE_VERSION, PYTHON_VERSION)
SNAKEMAKE_IMAGE = "quay.io/biocontainers/snakemake:{}_0".format(SNAKEMAKE_BASETAG)


def pytest_namespace():
    return {'snakemake_image': SNAKEMAKE_IMAGE}
