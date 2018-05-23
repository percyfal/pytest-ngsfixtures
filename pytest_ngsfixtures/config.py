# -*- coding: utf-8 -*-
"""Configuration settings for pytest-ngsfixtures"""
import os
import pathlib
import logging
from pytest_ngsfixtures import DATA_DIR

REF_DIR = DATA_DIR / "ref"
SAMPLES_DIR = DATA_DIR / "seq"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

refignore = ["Makefile"]
reflayout = {x.name:str(x) for x in REF_DIR.iterdir() if x.name not in refignore}

# Define sampleinfo
# TODO: Simplify this definition
# Columns are sample, pu, pop, batch, fastq, read, run, is_pool
sampleinfo = [
    ['CHS.HG00512', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS.HG00512_1.fastq.gz', '1', 'CHS.HG00512', False],
    ['CHS.HG00512', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS.HG00512_2.fastq.gz', '2', 'CHS.HG00512', False],
    ['CHS.HG00513', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS.HG00513_1.fastq.gz', '1', 'CHS.HG00513', False],
    ['CHS.HG00513', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS.HG00513_2.fastq.gz', '2', 'CHS.HG00513', False],
    ['CHS', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS_1.fastq.gz', '1', 'CHS', True],
    ['CHS', '010101_AAABBB11XX', 'CHS', 'p1', 'CHS_2.fastq.gz', '2', 'CHS', True],
    ['PUR.HG00731.A', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00731.A_1.fastq.gz', '1', 'PUR.HG00731.A', False],
    ['PUR.HG00731.A', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00731.A_2.fastq.gz', '2', 'PUR.HG00731.A', False],
    ['PUR.HG00731.B', '020202_AAABBB22XX', 'PUR', 'p2', 'PUR.HG00731.B_1.fastq.gz', '1', 'PUR.HG00731.B', False],
    ['PUR.HG00731.B', '020202_AAABBB22XX', 'PUR', 'p2', 'PUR.HG00731.B_2.fastq.gz', '2', 'PUR.HG00731.B', False],
    ['PUR.HG00731', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00731_1.fastq.gz', '1', 'PUR.HG00731', False],
    ['PUR.HG00731', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00731_2.fastq.gz', '2', 'PUR.HG00731', False],
    ['PUR.HG00733.A', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00733.A_1.fastq.gz', '1', 'PUR.HG00733.A', False],
    ['PUR.HG00733.A', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00733.A_2.fastq.gz', '2', 'PUR.HG00733.A', False],
    ['PUR.HG00733.B', '020202_AAABBB22XX', 'PUR', 'p2', 'PUR.HG00733.B_1.fastq.gz', '1', 'PUR.HG00733.B', False],
    ['PUR.HG00733.B', '020202_AAABBB22XX', 'PUR', 'p2', 'PUR.HG00733.B_2.fastq.gz', '2', 'PUR.HG00733.B', False],
    ['PUR.HG00733', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00733_1.fastq.gz', '1', 'PUR.HG00733', False],
    ['PUR.HG00733', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR.HG00733_2.fastq.gz', '2', 'PUR.HG00733', False],
    ['PUR', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR_1.fastq.gz', '1', 'PUR', True],
    ['PUR', '010101_AAABBB11XX', 'PUR', 'p1', 'PUR_2.fastq.gz', '2', 'PUR', True],
    ['YRI.NA19238', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI.NA19238_1.fastq.gz', '1', 'YRI.NA19238', False],
    ['YRI.NA19238', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI.NA19238_2.fastq.gz', '2', 'YRI.NA19238', False],
    ['YRI.NA19239', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI.NA19239_1.fastq.gz', '1', 'YRI.NA19239', False],
    ['YRI.NA19239', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI.NA19239_2.fastq.gz', '2', 'YRI.NA19239', False],
    ['YRI', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI_1.fastq.gz', '1', 'YRI', True],
    ['YRI', '010101_AAABBB11XX', 'YRI', 'p1', 'YRI_2.fastq.gz', '2', 'YRI', True]
]


# Sample layouts
layout = {'flat':
          {
              's1_1.fastq.gz': str(SAMPLES_DIR / 'CHS.HG00512_1.fastq.gz'),
              's1_2.fastq.gz': str(SAMPLES_DIR / 'CHS.HG00512_2.fastq.gz')
          },
          'sample': {
              'CHS/CHS.HG00512_010101_AAABBB11XX_1.fastq.gz': str(SAMPLES_DIR / 'CHS.HG00512_1.fastq.gz'),
              'CHS/CHS.HG00512_010101_AAABBB11XX_2.fastq.gz': str(SAMPLES_DIR / 'CHS.HG00512_2.fastq.gz')
          }
}
runs = ['CHS.HG00512', 'CHS.HG00513', 'PUR.HG00731.A', 'PUR.HG00731.B', 'PUR.HG00733.A', 'YRI.NA19238', 'YRI.NA19239']
layout['sample_run'] = {
    "{SM}/{PU}/{SM}_{PU}_{read}.fastq.gz".format(SM=sm, PU=pu, read=read): str(SAMPLES_DIR / fq) for sm, pu, pop, batch, fq, read, run, pool in sampleinfo if run in runs
}
layout['sample_project_run'] = {
    "{SM}/{BATCH}/{PU}/{SM}_{PU}_{read}.fastq.gz".format(SM=sm, PU=pu, BATCH=batch, read=read): str(SAMPLES_DIR / fq) for sm, pu, pop, batch, fq, read, run, pool in sampleinfo if run in runs
}

popruns = ['CHS', 'PUR', 'YRI']
layout['pop_sample'] = {
    "{POP}/{SM}/{SM}_{PU}_{read}.fastq.gz".format(POP=pop, SM=sm, PU=pu, read=read): str(SAMPLES_DIR / fq) for sm, pu, pop, batch, fq, read, run, pool in sampleinfo if run in popruns
}
layout['pop_sample_run'] = {
    "{POP}/{SM}/{PU}/{SM}_{PU}_{read}.fastq.gz".format(POP=pop, SM=sm, PU=pu, read=read): str(SAMPLES_DIR / fq) for sm, pu, pop, batch, fq, read, run, pool in sampleinfo if run in popruns
}
layout['pop_sample_project_run'] = {
    "{POP}/{SM}/{BATCH}/{PU}/{SM}_{PU}_{read}.fastq.gz".format(POP=pop, SM=sm, PU=pu, BATCH=batch, read=read): str(SAMPLES_DIR / fq) for sm, pu, pop, batch, fq, read, run, pool in sampleinfo if run in popruns
}
