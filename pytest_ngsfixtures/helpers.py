# -*- coding: utf-8 -*-
import yaml
import copy
from snakemake.io import expand
from pytest_ngsfixtures import ROOT_DIR

BIOCONDA="""channels:
  - bioconda
dependencies:
  - {application}=={version}
"""

def make_conda_env_file(output, conda=BIOCONDA, **kw):
    with open(output, "w") as fh:
        fh.write(conda.format(**kw))


def make_targets(rules, config, application, **kw):
    TARGETS = []
    for r in rules:
        p = {}
        if not r.name.startswith(application):
            continue
        if "{end}" in str(r.output):
            p['end'] = kw['end']
        if "{version}" in str(r.output):
            p['version'] = config[application][r.name].get('_versions', kw['version'])
        TMP = expand(r.output, **p)
        TARGETS = TARGETS + list(TMP)
    return TARGETS
