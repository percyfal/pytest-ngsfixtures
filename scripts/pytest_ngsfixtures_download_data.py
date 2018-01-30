#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse
from pytest_ngsfixtures import factories, ROOT_DIR

DATADIR = os.path.realpath(os.path.join(ROOT_DIR, "data", "{size}"))
DOWNLOAD_SIZES = ["small", "medium", "yuge"]

if int(sys.version[0]) != 3:
    logger.error("python version 3 required to run")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Download large ngsfixtures data")
parser.add_argument('-n', '--dry-run', action='store_true',
                    help="dry run", dest="dry_run")
parser.add_argument('-f', '--force', action='store_true',
                    help="force download", dest="force")
parser.add_argument('-s', '--size', action='store', default="small",
                    help="size of dataset", choices=DOWNLOAD_SIZES,
                    dest="size")

args = parser.parse_args()

filelist = []
for path, dirs, files in os.walk(DATADIR.format(size="tiny")):
    filelist = [os.path.join(DATADIR.format(size=args.size), x) for x in files]

for fn in filelist:
    factories.download_sample_file(fn, args.size, args.dry_run, args.force)
