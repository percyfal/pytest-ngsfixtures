# -*- coding: utf-8 -*-
# see https://developer.github.com/v3/repos/contents/#get-contents
import os
import sys
import re
import ast
import subprocess as sp
from pytest_ngsfixtures import __version__ as ngsfixtures_version, ROOT_DIR

GITHUB_API = 'https://api.github.com/repos/{user}/{repo}/contents/{path}'

BIOCONDA_CONFIG = u"""# Conda configuration file for {application}
#
# Generated by pytest_ngsfixtures_add_application.py,
# version {ngsfixtures_version}
#
# Application output is output to directories named according to
# version number ({{version}} format label) and possibly to
# subdirectories named after sequencing configuration, either paired
# end (pe) or single end (pe) ({{end}} format label)
#
# Applications are run from snakemake with the --use-conda option.
# This will generate a separate conda environment for each version.
# Conda environment files are generated on the fly, listing
# {application} as the sole dependency. In some cases additional
# depencies are required. Add these to the _conda_dependencies parameter
# below.
#
# The snakemake clean rule is defined in ../fileutils.sm. The _clean
# parameter lists additional file patterns targetted for removal.
#
# Finally, some subcommands aren't available for all versions of an
# application. It is possible to override the global _versions by
# adding _versions below the subcommand in question.
#
#
# TODO:
#
# 1. Set default version to the latest version number in case the
# proposed version is wrong
#
# 2. For each rule added to Snakefile, add a corresponding entry below
# with the format of the output file name.
#

{application}:
  _default: '{default}'
  _versions: {versions}
  _conda_versions: {conda_versions}
  _conda_dependencies: [] # Add extra conda dependencies required for this package here
  _clean: [] # Add clean file pattern here

  # {application}_rule1:
  #   output: "{{version}}/{{end}}/outputfile.ext"
  # {application}_rule2:
  #   output: "{{version}}/{{end}}/outputfile.ext"
  #   _versions: [] # add specific versions to subcommand if neede
  # and so on

"""

DEFAULT_CONFIG = u"""{application}:
  _default: {default}
  _versions: {versions}
"""

BIOCONDA_SNAKEFILE = u"""# -*- snakemake -*-
import os

configfile: "../config.yaml"
configfile: "config.yaml"

APPLICATION = "{application}"

param = {{
    'end': config['end'],
}}

# Add required inputfiles here, or specify separately for each rule.
# The conda parameter is required.
inputfiles = {{
    'conda': "{application}-{{version}}.yaml",
    # 'bam': os.path.join("../{{end}}", config['input']['bam']),
    # 'ref': os.path.join("../../ref", config['input']['ref']),
}}

# NB: the 'rule1', 'rule2' etc labels should preferably map to the
# subcommand name itself

rule {application}_rule1:
    input: **inputfiles
    output: config[APPLICATION]["{application}_rule1"]["output"]
    conda: APPLICATION + "-{{version}}.yaml"
    shell: "{application}"

rule {application}_rule2:
    input: **inputfiles
    output: config[APPLICATION]["{application}_rule2"]["output"]
    conda: APPLICATION + "-{{version}}.yaml"
    shell: "{application}"

# Include rules for making the output
include: "../fileutils.sm"
"""

DEFAULT_SNAKEFILE = u"""# -*- snakemake -*-
import os

configfile: "../config.yaml"
configfile: "config.yaml"

APPLICATION = "{application}"

param = {{
    'end': config['end'],
}}

# Add required inputfiles here, or specify separately for each rule.
inputfiles = {{
    # 'bam': os.path.join("../{{end}}", config['input']['bam']),
    # 'ref': os.path.join("../../ref", config['input']['ref']),
}}

# NB: the 'rule1', 'rule2' etc labels should preferably map to the
# subcommand name itself

rule {application}_rule1:
    input: **inputfiles
    output: config[APPLICATION]["{application}_rule1"]["output"]
    shell: "{application}"

rule {application}_rule2:
    input: **inputfiles
    output: config[APPLICATION]["{application}_rule2"]["output"]
    shell: "{application}"

# Include rules for making the output
include: "../fileutils.sm"
"""

def get_bioconda_info(application):
    output = sp.check_output(['conda', 'search', '-c', 'bioconda', '-f', application, '--json'])
    try:
        versions = sorted(set(re.findall('"version":\s+"([^ ]+)"', output.decode("utf-8"))))
        d = {'versions': versions,
             'conda_versions': versions,
             'default': versions[0],
             'application': application,
             'ngsfixtures_version': ngsfixtures_version,
        }
        return BIOCONDA_CONFIG.format(**d), BIOCONDA_SNAKEFILE.format(**d)
    except Exception as e:
        import traceback
        print(traceback.print_exc())
        raise e


def get_github_info(application, user, repo, path):
    d = {'user': user,
         'repo': repo,
         'path': path,
    }
    url = GITHUB_API.format(**d)
    import requests, json
    dd = requests.get(url)
    data = dd.json()
    versions = []
    for entry in data:
        if entry['type'] == "dir":
            versions.append(entry['name'])
    d = {'versions': sorted(versions),
         'default': sorted(versions)[0],
         'application': application,
    }
    return DEFAULT_CONFIG.format(**d), DEFAULT_SNAKEFILE.format(**d)


def get_other_info(application):
    return None, None


def create_feature_branch(application):
    """Checkout feature branch from develop.

    Will try to checkout develop and create feature branch for
    application. Fails if develop is dirty.

    """
    application_path = os.path.abspath(os.path.join("data", "applications"))
    feature_branch = "feature/application/{}".format(application)

    try:
        sp.check_output(['git', 'checkout', 'develop'])
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        sp.check_output(['git', 'checkout', '-b', feature_branch])
    except Exception as e:
        print(e)
        sys.exit(1)

    return os.path.join(application_path, application)