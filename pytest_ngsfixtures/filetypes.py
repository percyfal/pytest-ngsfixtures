# -*- coding: utf-8 -*-
#
# Predefine commonly used file types
#
from os.path import join, dirname, realpath
from pytest_ngsfixtures import factories

DATADIR = realpath(join(dirname(__file__), "data", "ref"))
DATADIR = realpath(join(dirname(__file__), "data", "applications"))

bam = factories.filetype(join(DATADIR, "PUR.HG00731.bam"))
ref_transcripts_bed12 = factories.filetype(join(DATADIR, "ref-transcripts.bed12"))
bed12 = ref_transcripts_bed12
ref_transcripts_genePred = factories.filetype(join(DATADIR, "ref-transcripts.genePred"))
genePred = ref_transcripts_genePred
ref_transcripts_gtf = factories.filetype(join(DATADIR, "ref-transcripts.gtf"))
gtf = ref_transcripts_gtf


filetypes = ['bam', 'bed12', 'ref_transcripts_bed12',
             'genePred', 'ref_transcripts_genePred',
             'gtf', 'ref_transcripts_gtf']

__all__ = filetypes + ['filetypes']
