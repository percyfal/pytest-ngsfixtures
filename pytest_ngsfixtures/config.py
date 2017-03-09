# -*- coding: utf-8 -*-
"""Configuration settings for pytest-ngsfixtures"""
import os
import yaml
import itertools
from collections import namedtuple
from pytest_ngsfixtures import ROOT_DIR, helpers

DATADIR = os.path.join(ROOT_DIR, "data", "applications")
configfile = os.path.join(DATADIR, "config.yaml")

Config = namedtuple('Config', 'SIZES SAMPLES POPULATIONS SAMPLE_LAYOUTS')

sample_conf = Config(
    SIZES=["tiny", "small", "medium", "yuge"],
    SAMPLES=['CHS.HG00512', 'CHS.HG00513', 'CHS',
             'PUR.HG00731', 'PUR.HG00733', 'PUR',
             'PUR.HG00731.A', 'PUR.HG00731.B',
             'PUR.HG00733.A', 'PUR.HG00733.B',
             'YRI.NA19238', 'YRI.NA19239', 'YRI'],
    POPULATIONS=["CHS", "PUR", "YRI"],
    SAMPLE_LAYOUTS=["sample", "sample_run",
                    "project_sample_run", "pop_sample",
                    "pop_sample_run", "pop_project_sample_run"]
)


def application_config():
    with open(configfile, 'r') as fh:
        application_config = yaml.load(fh)
    return application_config


def application_fixtures(use_conda_versions=True):
    """Return the application fixtures.

    Returns the application fixtures defined in the application config
    file (data/applications/config.yaml).

    Params:
      use_conda_versions (bool): use the conda versions for each application

    Returns:
      list of fixtures, where each entry consists of application,
      command, version, end, and the raw output.
    """
    fixtures = []
    conf = application_config()
    for app, d in conf.items():
        if app in ['basedir', 'end', 'input', 'params']:
            continue
        versions = helpers.get_versions(conf[app])
        for command, params in d.items():
            if command.startswith("_"):
                continue
            versions = helpers.get_versions(conf[app][command], versions)
            _raw_output = params["output"]
            _ends = ["se", "pe"]
            if isinstance(_raw_output, dict):
                if not any("{end}" in x for x in _raw_output.values()):
                    _ends = ["se"]
                output = itertools.product([app], [command],  versions, _ends, [v for k, v in _raw_output.items()])
            else:
                if "{end}" not in _raw_output:
                    _ends = ["se"]
                output = itertools.product([app], [command], versions, _ends, [_raw_output])
            fixtures.append(list(output))
    return [x for l in fixtures for x in l]
