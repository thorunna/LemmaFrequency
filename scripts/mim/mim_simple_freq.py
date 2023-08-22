"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the MÍM corpus. The output is a .tsv file containing
the following information:

    Lemma
    Word category, including the gender if the lemma in question is a noun
    The lemma's frequency

"""

from collections import Counter
import xml.etree.ElementTree
import csv
import sys
import operator
import re

# Directory where MIM is stored. This directory contains
# a fileList.txt file that is provided with the corpus and
# points to all the .xml files
basedir = "/Users/torunnarnardottir/Vinna/MIM/"
file_list = "{}fileList.txt".format(basedir)

# Path of output file
output_file = "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/mim_simple_freq.tsv"

# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}


def text_words(teifile):
    """
    Function to extract lemma occurances from tei xml file
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for aword in root.findall(".//tei:w", ns):
        lemma = aword.get("lemma")
        tag = aword.get("type")

        # handling for a unicode character in the MÍM files
        if lemma != " ":
            # if noun, include gender with tag
            if tag[0] == "n":
                tag = tag[:2]
            else:
                tag = tag[0]

            yield "{}\t{}".format(lemma, tag)


# counter object that updates frequencies for lemmas file by file
c = Counter()

with open(file_list) as f:
    # the file list included with the corpus is tab delimited
    reader = csv.DictReader(f, delimiter="\t")

    for text_count, item in enumerate(reader):
        folder = item["Folder"]
        fname = item["File Name"]
        full_fname = "{}{}/{}".format(basedir, folder, fname)

        # update counter with words from the current text
        c.update((text_words(full_fname)))

        # display progress
        sys.stdout.write("\rTexts processed: {}".format(text_count))
        sys.stdout.flush()

# finally, write blank line because of flush.
print()

# sort frequency list in reverse order by counts (most frequent first)
sorted_words = reversed(sorted(c.items(), key=operator.itemgetter(1)))

# make tab formatted entries for output file
allwords = ["{}\t{}".format(x[0], x[1]) for x in sorted_words]

# write output to file
with open(output_file, "w") as f:
    f.write("\n".join(allwords))
