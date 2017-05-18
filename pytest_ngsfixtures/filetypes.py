# -*- coding: utf-8 -*-
#
# Predefine commonly used file types
#
import yaml
from os.path import join, dirname, realpath
from pytest_ngsfixtures import factories

REFDIR = realpath(join(dirname(__file__), "data", "ref"))
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


CONFIGFILE = realpath(join(DATADIR, "config.yaml"))
with open(CONFIGFILE, "r") as fh:
    MAPPING = yaml.load(fh)

def filetype_mapping(ft, end="pe"):
    """Retrieve mapping for filetype to fixture file name.

    Params:
      ft (str): filetype
      end (str): sequencing mode

    Returns:
      str: fixture file names
    """
    if ft is None:
        return None
    try:
        fn = join(DATADIR, end, MAPPING['input'][ft])
    except Exception as e:
        raise e
    return fn

__all__ = filetypes + ['filetypes']
