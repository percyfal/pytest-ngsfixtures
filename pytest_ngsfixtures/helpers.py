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
            print("'_versions' key missing: ")
            print(e)
            raise
    for k in version_keys:
        versions = versions.intersection(subconfig.get(k, versions))
    return versions


def make_targets(rules, config, application, **kw):
    TARGETS = []
    all_versions = get_versions(config[application])
    for r in rules:
        p = {}
        if not r.name.startswith(application.replace("-", "_")):
            continue
        for label, out in r.output.items():
            if "{end}" in str(out):
                p['end'] = config[application][r.name].get("_end", kw['end'])
            if "{version}" in str(out):
                versions = get_versions(config[application][r.name], all_versions)
                p['version'] = versions
            TMP = expand(out, **p)
            TARGETS = TARGETS + list(TMP)
    return TARGETS
