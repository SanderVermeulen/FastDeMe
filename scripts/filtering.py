#!/usr/bin/python

import gzip, os, numpy, argparse, linecache, sys, multiprocessing, csv
from numpy import median
from Bio import SeqIO
from __main__ import *
if (args.trimming) == True:
  from QC import *
  

#BioBloomCategorizer definition

def BioBloomCat(prefix, input_R1, input_R2, input_SE):
  if (args.pe) and float(identity) > 0.8 and int(hashes) > 10:
    print "Contamination detected, running BioBloomCategorizer"
    os.system('{} --fq -e -t {} -p {} -f {} {} {}'.format(os.path.join(script_dir, "binaries/biobloomcategorizer"), args.threads, prefix, species + ".bf", os.path.join(output_dir, input_R1), os.path.join(output_dir, input_R2)))
    global BioBloomCategorizer
    BioBloomCategorizer = True
    os.system('mv {} {}'.format(prefix + "_noMatch_1.", prefix + "_noMatch_1.fastq"))
    os.system('mv {} {}'.format(prefix + "_noMatch_2.", prefix + "_noMatch_2.fastq"))
    print "Done"
  elif (args.pe) and float(identity) < 0.8 or int(hashes) < 10: 
    print "No contamination detected"
  
  
  
  if not (args.pe) and float(identity) > 0.8 and int(hashes) > 10:
    print "Contamination detected, running BioBloomCategorizer"
    os.system('{} --fq -t {} -p {} -f {} {}'.format(os.path.join(script_dir, "binaries/biobloomcategorizer"), args.threads, prefix, species + ".bf", os.path.join(output_dir, input_SE)))
    global BioBloomCategorizer
    BioBloomCategorizer = True
    print "Done"
    os.system('mv {} {}'.format(prefix + "_noMatch.", prefix + "_noMatch.fastq"))
  elif not (args.pe) and float(identity) < 0.8 or int(hashes) < 10:
    print "No contamination detected"
  
  if float(identity) < 0.8 and int(hashes) > 50:
    print "Contamination detected but unable to filter. Program will continue, but results might not be optimal"

print "Running mash screen"



if (args.pe):
  os.system('{} screen -w -p {} {} {} | sort -gr - | head > {}'.format(os.path.join(script_dir, "binaries/mash"), args.threads, os.path.join(script_dir, "db/mash_db/vertebrate.msh"), os.path.join(output_dir, trimmed_R1), "screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed_1.tab"))  
    
if not (args.pe):
  os.system('{} screen -w -p {} {} {} | sort -gr - | head > {}'.format(os.path.join(script_dir, "binaries/mash"), args.threads, os.path.join(script_dir, "db/mash_db/vertebrate.msh"), os.path.join(output_dir,trimmed_SE), "screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed.tab"))



print "Done"

if (args.pe):
  i = 1
  with open("{}".format("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed_1.tab", 'r')) as file_1:
    for row in csv.reader(file_1, delimiter='\t'):
      while i <= 1:
        identity = row[0]
        hashes = row[1]
        species = row[4]
        i += 1
  hashes=hashes.replace("/1000", "")

if not (args.pe):
  i = 1
  with open("{}".format("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed.tab", 'r')) as file_1:
    for row in csv.reader(file_1, delimiter='\t'):
      while i <= 1:
        identity = row[0]
        hashes = row[1]
        species = row[4]
        i += 1
  hashes=hashes.replace("/1000", "")


filter_exists = os.path.isfile(species + ".bf")
if filter_exists == False:
  print "filter not included in standard BioBloomCategorizer database, please download {} or turn off filtering"
  sys.exit()
  
BioBloomCategorizer = False

if noPrefix == True:
  BioBloomCat(args.prefix, trimmed_R1, trimmed_R2, trimmed_SE)


if noPrefix == False:
  BioBloomCat(args.prefix, trimmed_R1, trimmed_R2, trimmed_SE)


if noPrefix == True:
  
  if (args.pe) and BioBloomCategorizer == True:
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch_1.")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch_1."))
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch_2.")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch_2."))
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + "_1.")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + "_1."))
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + "_2.")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + "_2."))
  
  if not (args.pe) and BioBloomCategorizer == True:
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch.")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_multiMatch."))  
    if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + ".")):
      os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_" + os.path.basename(species) + "."))
  
  if os.path.exists(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", ""))) + "_summary.tsv"):
    os.remove(os.path.join(output_dir, os.path.basename(args.inp[0].replace(".fastq.gz", ""))) + "_summary.tsv")



if noPrefix == False:

  if (args.pe) and BioBloomCategorizer == True:
    if os.path.exists(os.path.join(output_dir, args.prefix + "_multiMatch_1.")):
      os.remove(os.path.join(output_dir, args.prefix + "_multiMatch_1."))
    if os.path.exists(os.path.join(output_dir, args.prefix + "_multiMatch_2.")):
      os.remove(os.path.join(output_dir, args.prefix + "_multiMatch_2."))
    if os.path.exists(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + "_1.")):
      os.remove(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + "_1."))
    if os.path.exists(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + "_2.")):
      os.remove(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + "_2."))
  
  if not (args.pe) and BioBloomCategorizer == True:
    if os.path.exists(os.path.join(output_dir, args.prefix + "_multiMatch.")):
      os.remove(os.path.join(output_dir, args.prefix + "_multiMatch."))
    if os.path.exists(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + ".")):
      os.remove(os.path.join(output_dir, args.prefix + "_" + os.path.basename(species) + "."))
  
  if os.path.exists(os.path.join(output_dir, args.prefix) + "_summary.tsv"):
    os.remove(os.path.join(output_dir, args.prefix) + "_summary.tsv")

if os.path.exists("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed.tab"):
  os.remove("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed.tab")

if os.path.exists("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed_1.tab"):
  os.remove("screen_" + os.path.basename(args.inp[0].replace(".fastq.gz", "")) + "_trimmed_1.tab")
      
       

    
     
     
  
  
  