# -*- coding: utf-8 -*-
from snakemake.io import expand

BIOCONDA = """channels:
  - bioconda
dependencies:
  - {application}=={version}
{extra}
"""


def make_conda_env_file(output, conda=BIOCONDA, **kw):
    with open(output, "w") as fh:
        fh.write(conda.format(**kw))


def get_versions(subconfig, versions=None, version_keys=['_versions', '_conda_versions']):
    if versions is None:
        try:
            versions = set(subconfig["_versions"])
        except KeyError as e:
            print("'_versions' key missing")
            raise
    for k in version_keys:
        versions = versions.intersection(subconfig.get(k, versions))
    return versions


def make_targets(rules, config, application, **kw):
    TARGETS = []
    versions = get_versions(config[application])
    for r in rules:
        p = {}
        if not r.name.startswith(application):
            continue
        if "{end}" in str(r.output):
            p['end'] = kw['end']
        if "{version}" in str(r.output):
            versions = get_versions(config[application][r.name], versions)
            p['version'] = versions
        TMP = expand(r.output, **p)
        TARGETS = TARGETS + list(TMP)
    return TARGETS