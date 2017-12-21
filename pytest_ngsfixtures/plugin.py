# -*- coding: utf-8 -*-
"""Plugin configuration module for pytest-ngsfixtures"""
import re
from pytest_ngsfixtures import factories
from pytest_ngsfixtures.fixtures import psample, pref
from pytest_ngsfixtures.config import sample_conf, runfmt_alias

_help_ngs_size = "select sample size (choices: {})".format(", ".join("'{}'".format(x) for x in sample_conf.SIZES))
_help_ngs_layout = "select predefined sample layout(s) (allowed choices: {})".format(", ".join("'{}'".format(x) for x in sample_conf.SAMPLE_LAYOUTS))
_help_ngs_show_fixture = "show fixture layout"
_help_ngs_threads = "set the number of threads to use in test"


def pytest_addoption(parser):
    group = parser.getgroup("ngsfixtures", "next-generation sequencing fixture options")
    group.addoption(
        '-X',
        '--ngs-size',
        action='store',
        dest='ngs_size',
        default='tiny',
        help=_help_ngs_size,
        choices=sample_conf.SIZES,
        metavar="size",
    )
    group.addoption(
        '-L',
        '--ngs-layout',
        action='store',
        dest='ngs_layout',
        default=["short"],
        help=_help_ngs_layout,
        nargs="+",
        metavar="layout",
        choices=sample_conf.SAMPLE_LAYOUTS,
    )
    group.addoption(
        "--ngs-pool",
        action="store_true",
        help="run tests on pooled data",
        default=False,
        dest="ngs_pool",
    )
    group.addoption(
        '-F',
        '--ngs-show-fixture',
        action="store_true",
        dest="ngs_show_fixture",
        default=False,
        help=_help_ngs_show_fixture,
    )
    group.addoption(
        '--nt',
        '--ngs-threads',
        action="store",
        dest="ngs_threads",
        default=1,
        help=_help_ngs_threads,
    )
    group.addoption(
        "--ngs-runfmt",
        action="store",
        help="sample test run format; organization of samples",
        default=["sample"],
        nargs="+",
        dest="ngs_runfmt",
        metavar="runfmt",
    )
    group.addoption(
        "--ngs-copy",
        action="store_true",
        help="copy test data instead of symlinking",
        default=False,
        dest="ngs_copy",
    )
    group.addoption(
        "--ngs-ref",
        action="store_true",
        help="use ref reference layout instead of scaffolds",
        default=False,
        dest="ngs_ref",
    )


def pytest_configure(config):
    config.option.ngs_runfmt_alias = config.option.ngs_runfmt
    config.option.ngs_layout = list(set(config.option.ngs_layout))
    runfmt = []
    if config.option.ngs_runfmt:
        for rf in config.option.ngs_runfmt:
            if re.search("[{}]", rf) is None:
                assert rf in sample_conf.RUNFMT_ALIAS, "if run format is given as string, must be one of {}".format(", ".join(sample_conf.RUNFMT_ALIAS))

            runfmt.append(runfmt_alias(rf)[1])
        config.option.ngs_runfmt = runfmt
    if config.option.ngs_pool:
        config.option.ngs_layout.append("pool")
    if "pool" in config.option.ngs_layout:
        config.option.ngs_pool = True


flat = factories.sample_layout(sample=['CHS.HG00512'],
                               scope="function", numbered=True,
                               dirname="flat")
ref = factories.reference_layout(dirname="ref")
scaffolds = factories.reference_layout(label="scaffolds",
                                       dirname="scaffolds")
