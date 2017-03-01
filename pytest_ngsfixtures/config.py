# -*- coding: utf-8 -*-
"""Configuration settings for pytest-ngsfixtures"""
from collections import namedtuple

Config = namedtuple('Config', 'SIZES SAMPLES POPULATIONS SAMPLE_LAYOUTS')

conf = Config(SIZES = ["tiny", "small", "medium", "yuge"],
              SAMPLES = ['CHS.HG00512', 'CHS.HG00513',
                         'PUR.HG00731', 'PUR.HG00733',
                         'PUR.HG00731.A', 'PUR.HG00731.B',
                         'PUR.HG00733.A', 'PUR.HG00733.B',
                         'YRI.NA19238', 'YRI.NA19239'],
              POPULATIONS = ["CHS", "PUR", "YRI"],
              SAMPLE_LAYOUTS= ["sample", "sample_run", "project_sample_run",
                               "pop_sample", "pop_sample_run", "pop_project_sample_run"]
)

