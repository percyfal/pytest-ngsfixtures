# -*- coding: utf-8 -*-
"""layout
----------------------------------

Utility functions for sample and reference layouts.

"""
import py
import itertools
from pytest_ngsfixtures.file import ReadFixtureFile, ReferenceFixtureFile

layouts = {
    'short': {
        'sample': ['PUR.HG00731.A', 'PUR.HG00731.B', 'PUR.HG00733.A'],
        'alias': ['s1', 's1', 's2'],
        'platform_unit': ['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'],
        'paired_end': [True] * 3, 'numbered': True,
    },
    'individual': {
        'sample': ['PUR.HG00731.A', 'PUR.HG00731.B', 'PUR.HG00733.A'] + ['CHS.HG00512', 'CHS.HG00513'] + ['YRI.NA19238', 'YRI.NA19239'],
        'alias': ['PUR.HG00731', 'PUR.HG00731', 'PUR.HG00733'] + ['CHS.HG00512', 'CHS.HG00513'] + ['YRI.NA19238', 'YRI.NA19239'],
        'platform_unit': ['010101_AAABBB11XX', '020202_AAABBB22XX', '010101_AAABBB11XX'] + ['010101_AAABBB11XX', '020202_AAABBB22XX'] * 2,
        'population': ['PUR'] * 3 + ['CHS'] * 2 + ['YRI'] * 2,
        'paired_end': [True] * 7,
        'batch': ["p1", "p2", "p1"] + ["p1", "p2"] * 2,
    },
    'pool': {
        'sample': ["CHS", "PUR", "YRI"],
        'alias': ["CHS.pool", "PUR.pool", "YRI.pool"],
        'population': ["CHS", "PUR", "YRI"],
        'platform_unit': ['010101_AAABBB11XX',
                          '020202_AAABBB22XX',
                          '010101_AAABBB11XX'],
        'paired_end': [True] * 3,
    }
}


def generate_sample_layouts(layout="short",
                            combinator=itertools.zip_longest,
                            **kwargs):
    """Generate list of sample layout structures.

    A sample layout structure is a dictionary holding metadata for a
    sample layout. The keys are samtools read group specifiers and
    some custom labels, consisting of 'POP', 'PU', 'SM', 'BATCH', and
    'PE'.


    Args:
      layout (str): layout name
      population (list): list of population names
      sample (list): list of sample names
      platform_unit (list): list of platform units
      batch (list): list of batch (project) names
      paired_end (list): list of booleans indicating if a sample run
                         is paired end (True) or single end (False)
      alias (list): list of sample alias names
      combinator (fun): function to combine population,
                        platform_units, samples, batches, and
                        paired_end

    """
    keys = ['population', 'platform_unit', 'sample', 'batch', 'paired_end', 'alias']
    config = {k: kwargs.get(k, [None]) for k in keys}
    if layout is not None:
        assert layout in layouts.keys(), "named layout must be one of {}".format(", ".format(layouts.keys()))
        config.update(layouts[layout])
    return [dict(zip(keys, p)) for p in combinator(*[config[k] for k in keys])]


def setup_sample_layout(path, layout=None, copy=False, sample_prefix="s",
                        runfmt="{SM}/{SM}_{PU}", use_short_sample_names=True,
                        **kwargs):
    """Setup sample layout.


    Args:
      path (py._path.local.LocalPath): :py:`~py._path.local.LocalPath` path where test files will be setup
      layout (str): predefined layout name
      copy (bool): copy test files instead of symlinking (required for dockerized tests)
      sample_prefix (str): sample prefix for short names
      kwargs (dict): arguments that are passed on to :py:`~pytest_ngsfixtures.layout.generate_sample_layouts`
    """
    ReadFixtureFile.reset()
    output = []
    layout_list = generate_sample_layouts(layout=layout, **kwargs)
    for l in layout_list:
        l.update({'use_short_sample_name': use_short_sample_names,
                  'prefix': sample_prefix})
        r1 = ReadFixtureFile(runfmt=runfmt, path=path, copy=copy, **l)
        r1.setup()
        output.append(r1)
        if l.get("paired_end", True):
            r2 = ReadFixtureFile(runfmt=runfmt, path=path, copy=copy,
                                 read=2, **l)
            r2.setup()
            output.append(r2)
    if kwargs.get("sampleinfo", False):
        info = [",".join(output[0].sampleinfo_keys)]
        for o in output:
            info.append(o.sampleinfo)
        path.join("sampleinfo.csv").write("\n".join(info) + "\n")
    return path


def setup_reference_layout(path, label="ref", copy=False, **kwargs):
    """Setup reference layout

    Wrapper to setup multiple reference files. Either choose between
    'ref' or 'scaffolds' label.

    Args:
      path (py._path.local.LocalPath): :py:`~py._path.local.LocalPath` path where reference test files will be setup
      label (str): reference fixture label ('ref' or 'scaffolds')
      copy (bool): copy fixture files instead of symlinking

    Returns:
      py._path.local.LocalPath: modified :py:`~py._path.local.LocalPath` object with test files setup

    """
    ref_dict = ReferenceFixtureFile().ref
    assert label in list(ref_dict.keys()), "label '{}' must be one of {}".format(label, ", ".join(list(ref_dict.keys())))
    flist = ref_dict[label] + ref_dict['_always']
    for dst in flist:
        if dst.basename in ["ref.chrom.sizes", "scaffolds.chrom.sizes"]:
            r = ReferenceFixtureFile(path.join("chrom.sizes"), src=dst)
        else:
            r = ReferenceFixtureFile(path.join(py.path.local(dst).basename))
        r.setup()
    return path
