# -*- coding: utf-8 -*-
"""Configuration settings for pytest-ngsfixtures"""
import os
import yaml
import itertools
import logging
from collections import namedtuple
from pytest_ngsfixtures import DATA_DIR, helpers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APPLICATION_DATA_DIR = os.path.join(DATA_DIR, "applications")
APPLICATION_BLACKLIST = ["pe", "se"]
APPLICATION_DIRECTORIES = sorted(
    [os.path.join(APPLICATION_DATA_DIR, x) for x in os.listdir(APPLICATION_DATA_DIR) if
     os.path.isdir(os.path.join(APPLICATION_DATA_DIR, x)) and x not in
     APPLICATION_BLACKLIST]
)
configfile = os.path.join(APPLICATION_DATA_DIR, "config.yaml")

Config = namedtuple('Config', 'SIZES SAMPLES POPULATIONS SAMPLE_LAYOUTS RUNFMT RUNFMT_ALIAS')

sample_conf = Config(
    SIZES=("tiny", "small", "medium", "yuge"),
    SAMPLES=('CHS.HG00512', 'CHS.HG00513', 'CHS',
             'PUR.HG00731', 'PUR.HG00733', 'PUR',
             'PUR.HG00731.A', 'PUR.HG00731.B',
             'PUR.HG00733.A', 'PUR.HG00733.B',
             'YRI.NA19238', 'YRI.NA19239', 'YRI'),
    POPULATIONS=tuple(["CHS"] * 3 +
                      ["PUR"] * 7 +
                      ["YRI"] * 3),
    SAMPLE_LAYOUTS=("short", "individual", "pool"),
    RUNFMT=("{SM}", "{SM}/{SM}_{PU}", "{SM}/{PU}/{SM}_{PU}", "{SM}/{BATCH}/{PU}/{SM}_{PU}",
            "{POP}/{SM}/{SM}_{PU}", "{POP}/{SM}/{PU}/{SM}_{PU}", "{POP}/{SM}/{BATCH}/{PU}/{SM}_{PU}"),
    RUNFMT_ALIAS=("flat", "sample", "sample_run", "sample_project_run", "pop_sample",
                  "pop_sample_run", "pop_sample_project_run")
)


def runfmt_alias(alias=None, runfmt=None):
    """Get alias and runformat tuple"""
    if alias is not None:
        try:
            i = sample_conf.RUNFMT_ALIAS.index(alias)
            runfmt = sample_conf.RUNFMT[i]
        except:
            pass
    elif runfmt is not None:
        try:
            i = sample_conf.RUNFMT.index(runfmt)
            alias = sample_conf.RUNFMT_ALIAS[i]
        except:
            pass
    return alias, runfmt


def application_config(application=None):
    """Get application configuration.

    Application output files are stored in the "data/applications"
    subdirectory of pytest-ngsfixtures installation directory. Every
    application lives in its own subdirectory named after the
    application.

    The application configuration is a dictionary that merges a
    top-level configuration file 'config.yaml' with
    application-specific 'config.yaml' files residing in the
    application directories. The general configuration defines keys
    'basedir', 'end', 'input', and 'params'. The application
    configuration sets metadata used by snakemake to auto-generate
    application data output.

    Args:
      application (str): application name

    Return:
      dict: application configuration

    Example:

      Retrieve application configuration and use it to generate a
      fixture. See also
      :mod:`~pytest_ngsfixtures.factories.application_output`.

      >>> from pytest_ngsfixtures import config
      >>> conf = config.application_config()
      >>> # Application rule metadata are formatted as python miniformat strings
      >>> conf['qualimap']['qualimap_bamqc_pe']['output']['genome_results']
      '{version}/{end}/genome_results.txt'

    """
    with open(configfile, 'r') as fh:
        application_config = yaml.load(fh)
    for appdir in APPLICATION_DIRECTORIES:
        if application is not None:
            if os.path.basename(appdir) != application:
                continue
        cfile = os.path.join(appdir, "config.yaml")
        try:
            with open(cfile, 'r') as fh:
                conf = yaml.load(fh)
            application_config.update(conf)
        except Exception as e:
            print(e)

    return application_config


def get_application_fixture_output(application, command, version, end="se"):
    """Retrieve application output names as mapping from snakemake rule
    keyword to output file name.

    An application configuration file defines snakemake rule metadata
    such as output. The output section simply maps a rule keyword to
    an output file name. This function returns a key-value mapping
    from keyword to *formatted* output file name.

    Args:
      application (str): application name
      command (str): command name
      version (str): version
      end (str): se or pe

    Returns:
      dict: dictionary that maps snakemake rule keywords to formatted
            application output strings

    Example:

      >>> from pytest_ngsfixtures import config
      >>> af = config.get_application_fixture_output('qualimap', 'qualimap_bamqc_pe', '2.2.2')
      >>> print(list(af.keys())[0:2])
      ['genome_results', 'coverage_across_reference']
      >>> print(af['genome_results'])
      qualimap/2.2.2/se/genome_results.txt

    """
    conf = application_config(application)
    try:
        output = conf[application][command]['output']
    except KeyError as e:
        logging.error("[pytest_ngs]KeyError: {}".format(e))
        raise
    return {k: os.path.join(application, o.format(version=version, end=end)) for k, o in output.items()}


def flattened_application_fixture_metadata(application=None, end=None, version=None):
    """Return the application fixture metadata flattened as a list of tuples.

    Returns the application fixture metadata defined in the
    application config file (data/applications/config.yaml) as a list
    of tuples.

    Args:
      application (str): application name
      end (str): sequence configuration (single end/paired end)
      version (str): version identifier

    Returns:
      flattened list of fixture metadata, where each entry consists of
      application, command, version, end, and the raw unformatted output.

    Example:

      Typically this function is used to collect all metadata needed
      to setup a (parametrized) pytest fixture. See
      :py:mod:`bioodo.tests.utils.fixture_factory` for an example
      where a list of fixture metadata is used to generate a set of
      parametrized fixtures.

      >>> from pytest_ngsfixtures import config
      >>> af = config.flattened_application_fixture_metadata(application="qualimap")
      >>> module, command, version, end, fmtdict = af[0]
      >>> module, command, version, end
      ('qualimap', 'qualimap_bamqc_pe', '2.2.2', 'pe')
      >>> fmtdict['genome_results']
      '{version}/{end}/genome_results.txt'

    """
    fixtures = []
    conf = application_config(application)
    for app, d in conf.items():
        if app in ['basedir', 'end', 'input', 'params']:
            continue
        if application is not None and app != application:
            continue
        all_versions = helpers.get_versions(conf[app]) if version is None else set([version])
        for command, params in d.items():
            if command.startswith("_"):
                continue
            versions = helpers.get_versions(conf[app][command], all_versions)
            _raw_output = params["output"]
            if end is None:
                _ends = [params["_end"]] if "_end" in params.keys() else ["se", "pe"]
            else:
                if "_end" in params.keys() and params["_end"] != end:
                    continue
                _ends = [end]
            if isinstance(_raw_output, dict):
                if not any("{end}" in x for x in _raw_output.values()):
                    _ends = ["se"]
                output = itertools.product([app], [command], versions, _ends, [_raw_output])
            else:
                if "{end}" not in _raw_output:
                    _ends = ["se"]
                output = itertools.product([app], [command], versions, _ends, [_raw_output])
            fixtures.append(list(output))
    return [x for l in fixtures for x in l]
