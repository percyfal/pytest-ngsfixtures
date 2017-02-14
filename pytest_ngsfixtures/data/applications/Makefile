#!/usr/bin/make -rRf
SHELL=/bin/sh
.DELETE_ON_ERROR:

##############################
# Prerequisite temporary files
#
# - large bams for parsing
##############################
BWA=bwa

ref.fasta: ../ref/ref.fasta
	ln -s $<

ref.fasta.sa: ref.fasta
	$(BWA) index $<

%.bam: ref.fasta ../yuge/%_1.fastq.gz ../yuge/%_2.fastq.gz ref.fasta.sa

test.bam: ../yuge
