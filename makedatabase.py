#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import argparse
import logging
import subprocess
from multiprocessing import Pool

""" 
@author:yueyao 
@file: makedatabase.py 
@time: 2018/06/10 
"""

class Software(object):
    def __init__(self):
        self.HISAT2=""
        self.BOWTIE2=""
        self.SAMTOOLS=""
        self.PICARD=""
        self.RSEM=""
        self.DIAMOND=""

def run_cmd(cmd):
    print('Run cmd %s' % cmd)
    submit = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                              universal_newlines=True)
    submit.communicate()

def showhelp():
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    help="""
        this program is use to build index for genome or annotation for gene cds. please use -h parameter to check detail
    """
    logger.info("%s",help)

def cmd_run_para(cmd):
    processNum = len(cmd)
    print("running start")
    with Pool(processNum) as p:
        for j in range(len(cmd)):
            p.apply_async(run_cmd, args=(cmd[j],))
        p.close()
        p.join()
        print("All subprocess done")

def get_database_path(species,tyclass):
    database={
        'an':{
            "keggdb":"",
            "nrdb":"",
            'go_obo':"",
            "accession2go":""
        },
        'pl':{
            "keggdb":"",
            "nrdb":"",
            'go_obo':"",
            "accession2go":""
        },
        "fg":{
            "keggdb":"",
            "nrdb":"",
            'go_obo':"",
            "accession2go":""
        }
    }
    return database[species][tyclass]


def format_ncbi_gff(gff):
    gff_file=open(gff,'r')
    line = gff_file.readlines()
    gff_file.close()

if __name__=='__main__':
    if len(sys.argv) == 1 :
        showhelp()
        sys.exit()

    pwd = os.path.abspath('.')
    parser = argparse.ArgumentParser(description="make database help")
    parser.add_argument('--mode', dest='runMode', type=str,
                        help='how to action: genomeindex/geneannotation/both')
    parser.add_argument('--outdir', dest='outdir', type=str, default=pwd,
                        help='the output directory,default current directory')
    parser.add_argument('--genomefa', dest='genomeFa', type=str,
                        help="the genome fa used in workflow.\n ")
    parser.add_argument('--goannot', dest='goannot', type=str,
                        help="the go annot file used in workflow.\n ")
    parser.add_argument('--cdsfa', dest='cdsFa', type=str,
                        help="the genome fa used in workflow.\n")
    parser.add_argument('--species', dest='species', type=str,
                        help="set species name where needed,for example an,pl,fg.\n")
    parser.add_argument('--prefix', dest='prefix', type=str,
                        help="set prefix name for genome and gene index file.\n")

    localeArg = parser.parse_args()
    os.makedirs(localeArg.outdir,exist_ok=True)
    if localeArg.runMode is None or localeArg.species is None:
        print("need set --mode")
        sys.exit()
    soft=Software()
    genomeindexcmd="{hisat2} {genomefa} {outdir}/{prefix}.genome.fa\n" \
             "{samtools} faidx {genomefa} {outdir}/{prefix}.genome.fa.fai\n" \
             "{picard} R={genomefa} O={outdir}/{prefix}.genome.dict".format(
             hisat2=soft.HISAT2,
             genomefa=localeArg.genomeFa,
             outdir=localeArg.outdir,
             prefix=localeArg.prefix,
             samtools=soft.SAMTOOLS,
             picard=soft.PICARD)
    genomeindexlist=genomeindexcmd.split('\n')

    keggdb=get_database_path(str(localeArg.species),'keggdb')
    go_obo=get_database_path(str(localeArg.species),'go_obo')
    nrdb=get_database_path(str(localeArg.species),'nrdb')
    gene2go=get_database_path(str(localeArg.species),'accession2go')
    geneannocmd="{diamond} blastx --evalue 1e-5 --threads 20 --outfmt 5 --max-target-seqs 5 --more-sensitive -b 0.5 --salltitles -d " \
                "{keggdb} -q {cdsfa} -o {outdir}/{prefix}.cds.fa.blast.nr;" \
                "sed -i 's/>diamond .*</>BLASTX 2.2.28+</g' {outdir}/{prefix}.cds.fa.blast.nr;" \
                "perl blast_m7_parser.pl {outdir}/{prefix}.cds.fa.blast.nr {outdir}/{prefix}.cds.fa.blast.tab;" \
                "python BLAST3GO.py --NR_tab {outdir}/{prefix}.cds.fa.blast.tab --Accession_go {gene2go} --output {outdir}/{prefix}.annot;" \
                "perl annot2goa.pl {go_obo} {outdir}/{prefix}.annot {outdir}/{prefix};" \
                "perl blast_m7_m8.pl -input {outdir}/{prefix}.cds.fa.blast.nr -output {outdir}/{prefix}.nr.m8;" \
                "perl getNrDesc.pl -input {outdir}/{prefix}.nr.m8 -rank 1 -nr {nrdb} -output {outdir}/{prefix}.nr.desc\n" \
                "{diamond} blastx --evalue 1e-5 --threads 20 --outfmt  6 --seg no   --max-target-seqs 5 --more-sensitive -b 0.2 --salltitles -d " \
                "{keggdb} -q {cdsfa} {outdir}/{prefix}.cds.fa.blast.kegg;" \
                "perl blast2ko.pl -input {cdsfa}  -output {outdir}/{prefix}.ko -blastout {outdir}/{prefix}.cds.fa.blast.kegg -kegg {keggdb}".format(
                diamond=soft.DIAMOND,
                cdsfa=localeArg.cdsFa,
                outdir=localeArg.outdir,
                prefix=localeArg.prefix,
                keggdb=keggdb,
                nrdb=nrdb,
                gene2go=gene2go,
                go_obo=go_obo
    )
    geneannotationcmd=geneannocmd.split('\n')


    if localeArg.runMode == 'genomeindex':
        if localeArg.genomeFa is None or localeArg.prefix is None:
            print("need set prefix and genome to genomeindex")
            sys.exit()
        else:
            cmd_run_para(genomeindexlist)
    elif localeArg.runMode == 'geneannotation':
        if localeArg.cdsFa is None or localeArg.prefix is None or localeArg.species is None:
            print("need set prefix, cdsfa, species to geneannotation")
            sys.exit()
        else:
            cmd_run_para(geneannotationcmd)
    elif localeArg.runMode == 'both':
        if localeArg.genomeFa is None or localeArg.prefix is None or localeArg.cdsFa is None or localeArg.prefix is None or localeArg.species is None:
            print("need set refix, cdsfa, species,prefix,genome to both")
            sys.exit()
        else:
            cmd_run_para(genomeindexlist)
            cmd_run_para(geneannotationcmd)
    else:
        print("Unknow mode ==> %s" % (localeArg.runMode))
