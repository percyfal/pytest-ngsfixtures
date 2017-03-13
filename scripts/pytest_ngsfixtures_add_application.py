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
from pytest_ngsfixtures import applications, ROOT_DIR

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


def setup(application, source):
    path = applications.create_feature_branch(application)
    config, snakefile = get_info(application, source)

    if not os.path.exists(path):
        os.mkdir(path)

    configfile = os.path.join(path, "config.yaml")
    with open(configfile, "w") as fh:
        fh.write(config)
    snakefile_path = os.path.join(path, "Snakefile")
    with open(snakefile_path, "w") as fh:
        fh.write(snakefile)

    print()
    print("all set to go!")
    print("start adding rules to {} and modify {} accordingly".format(snakefile_path, configfile))
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
    setup(args.application, args.source)
