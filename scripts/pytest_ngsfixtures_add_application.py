#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest_ngsfixtures_add_application.py
-------------------------------------

Add application data to pytest_ngsfixtures.
"""
import os
import sys
import argparse
import subprocess as sp
import logging
from pytest_ngsfixtures import applications, ROOT_DIR

logger = logging.getLogger(__name__)

SOURCES = ["bioconda", "github", "other"]

if int(sys.version[0]) != 3:
    logger.error("python version 3 required to run")
    sys.exit(1)


def get_info(application, source):
    if source == "bioconda":
        return applications.get_bioconda_info(application)
    elif source == "github":
        return applications.get_github_info(application)
    elif source == "other":
        return applications.get_other_info(application)


def setup(application, source, dry_run=False):
    path = applications.create_feature_branch(application, dry_run)
    config, snakefile = get_info(application, source)

    if not os.path.exists(path):
        os.mkdir(path)

    configfile = os.path.join(path, "config.yaml")
    snakefile_path = os.path.join(path, "Snakefile")

    if dry_run:
        logger.dry_run("setup new application directory {}".format(path))
        logger.dry_run("saving {} and {}".format(configfile, snakefile_path))
    else:
        with open(configfile, "w") as fh:
            fh.write(config)
        with open(snakefile_path, "w") as fh:
            fh.write(snakefile)

    print()
    print("All set to go!")
    print()
    print("  1. cd to {}".format(path))
    print("  2. Start adding rules to {} and modify {} accordingly".format(os.path.basename(snakefile_path),
                                                                           os.path.basename(configfile)))
    print("  3. run 'snakemake conda' to generate conda files")
    print("  4. run 'snakemake --use-conda all' to generate output")
    print("  5. (optional): run 'snakemake clean' to remove excess output")
    print("  6. run 'git add Snakefile config.yaml FILENAMES' to add output")
    print("  7. submit pull request to https://github.com/percyfal/pytest-ngsfixtures")
    print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Setup application files for generating test data")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="dry run", dest="dry_run")
    parser.add_argument('-s', '--source', action='store', default="bioconda",
                        help="application source", choices=SOURCES, dest="source")
    parser.add_argument('application', action='store',
                        help="application name")


    args = parser.parse_args()
    setup(args.application, args.source, args.dry_run)
