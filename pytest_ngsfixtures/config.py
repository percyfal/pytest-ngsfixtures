# -*- coding: utf-8 -*-
"""Configuration settings for pytest-ngsfixtures"""
import os
import yaml
from collections import namedtuple
from pytest_ngsfixtures import ROOT_DIR

DATADIR = os.path.join(ROOT_DIR, "data", "applications")
configfile = os.path.join(DATADIR, "config.yaml")

Config = namedtuple('Config', 'SIZES SAMPLES POPULATIONS SAMPLE_LAYOUTS')

sample_conf = Config(SIZES = ["tiny", "small", "medium", "yuge"],
              SAMPLES = ['CHS.HG00512', 'CHS.HG00513', 'CHS',
                         'PUR.HG00731', 'PUR.HG00733', 'PUR',
                         'PUR.HG00731.A', 'PUR.HG00731.B',
                         'PUR.HG00733.A', 'PUR.HG00733.B',
                         'YRI.NA19238', 'YRI.NA19239', 'YRI'],
              POPULATIONS = ["CHS", "PUR", "YRI"],
              SAMPLE_LAYOUTS= ["sample", "sample_run", "project_sample_run",
                               "pop_sample", "pop_sample_run", "pop_project_sample_run"]
)


with open(configfile, 'r') as fh:
    application_config = yaml.load(fh)
