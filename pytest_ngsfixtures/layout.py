# -*- coding: utf-8 -*-
"""layout
----------------------------------

Utility functions for sample and reference layouts.

"""
import itertools
from pytest_ngsfixtures.file import ReadFixtureFile

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


def sample_fixture_layout(p, layout=None, copy=False, sample_prefix="s",
                          runfmt="{SM}/{SM}_{PU}", use_short_sample_names=True,
                          **kwargs):
    """Setup sample fixture layout.


    Args:
      p (py._path.local.LocalPath): :py:`~py._path.local.LocalPath` path where test files will be setup
      layout (str): predefined layout name
      copy (bool): copy test files instead of symlinking (required for dockerized tests)
      sample_prefix (str): sample prefix for short names
    """
    if layout is not None:
        layout_list = generate_sample_layouts(layout=layout)
    else:
        layout_list = generate_sample_layouts(**kwargs)
    for l in layout_list:
        l.update({'use_short_sample_names': use_short_sample_names,
                  'prefix': sample_prefix})
        r1 = ReadFixtureFile(runfmt=runfmt, path=p, copy=copy, **l)
        r1.setup()
        if kwargs.get("paired_end", True):
            r2 = ReadFixtureFile(runfmt=runfmt, path=p, copy=copy,
                                 read=2, **l)
            r2.setup()
    return p
