#!/usr/bin/make -rRf
SHELL=/bin/sh
.DELETE_ON_ERROR:

ECHO=echo
SED=sed

BCFTOOLS=bcftools
BEDTOOLS=bedtools
GENEPREDTOBED=genePredToBed
GTFTOGENEPRED=gtfToGenePred
PICARD=picard
PICARD_OPTIONS="VALIDATION_STRINGENCY=SILENT"
SAMTOOLS=samtools
TABIX=tabix


# Region with HLA-DQA2
TINY_REF_REGIONS=chr6:890000-900000 chr6:1940000-1960000
TINY_SCAFFOLD_REGIONS=scaffold1:890000-900000 scaffold9:0-20000

tiny-ref-gtf.bed:
	@$(ECHO) ${TINY_REF_REGIONS} | tr " " "\n" | $(SED) -e "s/[:-]/\t/g" > $@

tiny-scaffolds-gtf.bed:
	@$(ECHO) ${TINY_SCAFFOLD_REGIONS} | tr " " "\n" | $(SED) -e "s/[:-]/\t/g" > $@

##############################
# Implicit rules
##############################
%.dict: %.fa
	@if [ -e $@ ]; then $(RM) $@; fi;
	$(PICARD) CreateSequenceDictionary $(PICARD_OPTIONS)  R=$< O=$@

%.fa.fai: %.fa
	$(SAMTOOLS) faidx $<

# To avoid circular dependency create interval list from dict, using
# entire chromosomes as intervals
%.interval_list: %.dict
	cat $< > $@;
	cat $< | sed -e "s/\(LN:\|SN:\)//g" | grep "@SQ" | awk '{printf("%s\t%s\t%s\t%s\t%s\n", $$2, 1, $$3,"+","."); FS="\t"}' >> $@

%.bedGraph: %.bed chrom.sizes
	$(BEDTOOLS) genomecov -bg -trackline -trackopts name=$* -i $< -g $(word 2,$^) > $@

%.bed12: %.genePred
	$(GENEPREDTOBED) $< $@

%.bed: %.interval_list
	$(PICARD) IntervalListToBed $(PICARD_OPTIONS) I=$< O=$@

%.genePred: %.gtf
	$(GTFTOGENEPRED) -ignoreGroupsWithoutExons $< $@

# https://www.snip2code.com/Snippet/77082/Convert-gene-annotations-from-GTF-to-gen
%.refFlat: %.gtf
	$(GTFTOGENEPRED) -genePredExt -geneNameAsName2 -ignoreGroupsWithoutExons $< $@.tmp
	paste <(cut -f 12 $@.tmp) <(cut -f 1-10 $@.tmp) > $@

%-targets.bed: %-transcripts.gtf
	cat $< | awk '{if ($$3 == "gene") printf("%s\t%s\t%s\t%s\t%s\t%s\n",  $$1, $$4, $$5, $$6, 0, $$7); }' | head > $@

%-targets.interval_list: %-transcripts.gtf %.dict
	$(PICARD)  BedToIntervalList $(PICARD_OPTIONS) I=$(<:%-transcripts.gtf=%-targets.bed) O=$@ SD=$(word 2,$^)

BWA=bwa

ref.fa.sa: ref.fa
	$(BWA) index $<

scaffolds.fa.sa: scaffolds.fa
	$(BWA) index $<

%.ref.bam: ref.fa ../yuge/%_1.fastq.gz ../yuge/%_2.fastq.gz ref.fa.sa
	$(BWA) mem -R '@RG\tID:$*\tSM:$*' $(word 1, $^) $(word 2, $^) $(word 3, $^) 2> $*.mem.log | $(SAMTOOLS) view -Sb - > $@

%.sort.bam: %.bam
	$(SAMTOOLS) sort  $< -o $@

known.ref.bam: PUR.HG00731.ref.sort.bam PUR.HG00733.ref.sort.bam
	$(SAMTOOLS) merge -f $@ $^

%.scaffolds.bam: scaffolds.fa ../yuge/%_1.fastq.gz ../yuge/%_2.fastq.gz scaffolds.fa.sa
	$(BWA) mem -R '@RG\tID:$*\tSM:$*' $(word 1, $^) $(word 2, $^) $(word 3, $^) 2> $*.mem.log | $(SAMTOOLS) view -Sb - > $@

known.scaffolds.bam: PUR.HG00731.scaffolds.sort.bam PUR.HG00733.scaffolds.sort.bam
	$(SAMTOOLS) merge -f $@ $^

%.bam.bai: %.bam
	$(SAMTOOLS) index $<

%.scaffolds.vcf.gz: %.scaffolds.bam %.scaffolds.bam.bai scaffolds.fa
	$(SAMTOOLS) mpileup -ug -f $(word 3,$^) $(word 1, $^) | $(BCFTOOLS) call -vmO v | $(BCFTOOLS) filter -i'%QUAL>400' - > $@

%.ref.vcf.gz: %.ref.bam %.ref.bam.bai ref.fa
	$(SAMTOOLS) mpileup -ug -f $(word 3,$^) $(word 1, $^) | $(BCFTOOLS) call -vmO v  | $(BCFTOOLS) filter -i'%QUAL>400' - > $@

%-transcripts-tiny.gtf: %-transcripts.gtf tiny-%-gtf.bed
	$(BEDTOOLS) intersect -a $< -b $(word 2,$^) > $@

%.vcf.gz.tbi: %.vcf.gz
	$(TABIX) $<

knownsites: known.scaffolds.vcf.gz known.ref.vcf.gz

##############################
# Reference database
##############################
# ref.fa :: ../ref.fasta
# 	cp $< $@

ref: ref.bed ref.dict ref.fa ref.fa.fai ref.gtf ref.interval_list ref-targets.bed  ref-targets.interval_list

##############################
# Ref transcripts
##############################
# ref-transcripts.gtf :: ../ref.gtf
# 	cp $< $@

reftranscripts:  ref-transcripts.bed12 ref-transcripts.genePred ref-transcripts.gtf ref-transcripts-tiny.bed12 ref-transcripts-tiny.genePred ref-trancripts-tiny.gtf

##############################
# Reference
#
# Define scaffolds
#
##############################
# Scaffold lengths
# Last scaffold for sure contains a gene
SCAFFOLDLEN = 1050000 340000 230000 130000 20000 100000 40000 30000 20000 10000 10000 10000 10000

chrom.sizes:
	@if [ -e $@ ] ; then \
	$(RM) $@ ; \
	fi ;
	@start=0; end=0; i=1; \
	for l in $(SCAFFOLDLEN); do \
		end=`expr $$end + $$l` ; \
		len=`expr $$end - $$start`; \
		echo "scaffold$$i\t$$len" >> $@; \
		start=`expr $$start + $$l` ; \
		i=`expr $$i + 1` ; \
	done


chr6scaffolds.bed:
	@if [ -e $@ ] ; then \
	$(RM) $@ ; \
	fi ;
	@start=0; end=0; \
	for l in $(SCAFFOLDLEN); do \
		end=`expr $$end + $$l` ; \
		echo "chr6\t$$start\t$$end" >> $@; \
		start=`expr $$start + $$l` ; \
	done

chr6scaffoldends.bed: chr6scaffolds.bed
	cat $< | awk '{print $$1, $$2, $$2 + 1};' > $@


# Rule to generate reference with scaffolds
scaffolds.fa: ref.fa chr6scaffolds.bed
	$(BEDTOOLS) getfasta -fi $< -bed $(word 2,$^) | sed -e "s/>[^ ][^ ]*/>scaffold1/g" | awk '/scaffold/{sub("[0-9]+",++i)}1' > $@

# Rule to generate bed file that defines regions with N's
scaffoldsN.bed: scaffolds.chrom.sizes scaffolds-transcripts.gtf scaffolds.bed
	$(BEDTOOLS) random -seed 42 -g $(word 1,$^) -l 50 -n 100 > tmp.bed
	$(BEDTOOLS) random -seed 242 -g $(word 1,$^) -l 100 -n 50 >> tmp.bed
	$(BEDTOOLS) random -seed 24242 -g $(word 1,$^) -l 200 -n 20 >> tmp.bed
	$(BEDTOOLS) random -seed 4242 -g $(word 1,$^) -l 500 -n 10 >> tmp.bed
	$(BEDTOOLS) slop -b 100 -i $(word 2,$^) -g $(word 1,$^) | $(BEDTOOLS) subtract -a $(word 3,$^) -b - | $(BEDTOOLS) intersect -a - -b tmp.bed | $(BEDTOOLS) sort -i - | $(BEDTOOLS) merge -i - > $@

# Rule to generate reference with scaffolds and random N's
scaffoldsN.fa: scaffolds.fa scaffoldsN.bed
	$(BEDTOOLS) maskfasta -fi $< -fo $@ -bed $(word 2,$^)

# Rule to generate gtf
# Scaffold breaks have been chosen so that removing entries that span
# scaffold breaks is avoided
ref.genome:
	@$(ECHO) "chrom\tsize\nchr6\t$$(( $(REGIONEND) - $(REGIONSTART) + 1))" > $@

scaffolds-transcripts.gtf: ref-transcripts.gtf ref.genome
	@if [ -e $@ ] ; then \
	$(RM) $@ ; \
	fi ;
	@start=0; end=0; i=1; \
	for l in $(SCAFFOLDLEN); do \
		end=`expr $$end + $$l` ; \
		$(ECHO) "chr6\t$$start\t$$end" > tmp.bed; \
		$(BEDTOOLS) intersect -a $< -b tmp.bed | $(BEDTOOLS) shift -i - -g $(word 2,$^) -s -$$start | sed -e "s/chr6/scaffold$$i/g" >> $@ ; \
		start=`expr $$start + $$l` ; \
		i=`expr $$i + 1`; \
	done ; \
	$(RM) tmp.bed;


scaffolds: scaffolds.bed scaffolds.dict scaffolds.fa scaffolds.fa.fai scaffolds-transcripts.gtf scaffolds.interval_list scaffolds-targets.bed  scaffolds-targets.interval_list

scaffoldstranscripts:  scaffolds-transcripts.bed12 scaffolds-transcripts.genePred scaffolds-transcripts.gtf scaffolds-transcripts-tiny.bed12 scaffolds-transcripts-tiny.genePred scaffolds-transcripts-tiny.gtf

scaffoldsN: scaffoldsN.bed scaffoldsN.chrom.sizes scaffoldsN.dict scaffoldsN.fa scaffoldsN.fa.fai

.PHONY: all ref reftranscripts scaffolds scaffoldstranscripts knownsites

all: ref reftranscripts scaffolds scaffoldstranscripts scaffoldsN chrom.sizes knownsites

clean:
	$(RM) chr6*
	$(RM) tmp.bed
	$(RM) ref.genome
	$(RM) ref.fa.*
	$(RM) scaffolds.fa.*
	$(RM) PUR*
	$(RM) all*
	$(RM) tiny-*
	$(RM) nregions*
