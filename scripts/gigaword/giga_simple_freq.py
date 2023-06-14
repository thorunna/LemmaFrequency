"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the Gigaword Corpus. The output is a .tsv file containing
the following information:

    Lemma
    Word category, including the gender if the lemma in question is a noun
    The lemma's frequency

"""

from collections import Counter
import xml.etree.ElementTree
import os
import glob
import csv
import sys
import operator

# Directory where the Gigaword Corpus is stored.
file_list = [
    os.path.abspath(filename)
    for filename in glob.glob(
        "/Users/torunnarnardottir/Vinna/rmh/**/*.xml",
        recursive=True,
    )
]

# Path of output file
output_file = (
    "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/giga_simple_freq.tsv"
)

# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}


def text_words(teifile):
    """
    Function to extract lemma occurances from tei xml file
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for aword in root.findall(".//tei:w", ns):
        lemma = aword.get("lemma")
        tag = aword.get("pos")

        if lemma is None:
            print(teifile, lemma, tag)

        # if noun, include gender with tag
        if tag[0] == "n":
            tag = tag[:2]
        else:
            tag = tag[0]

        yield "{}\t{}".format(lemma, tag)


# counter object that updates frequencies for lemmas file by file
c = Counter()

print("Processing texts...")
for file in sorted(file_list):
    with open(file, "r"):
        # update counter with words from the current text
        c.update((text_words(file)))

# sort frequency list in reverse order by counts (most frequent first)
sorted_words = reversed(sorted(c.items(), key=operator.itemgetter(1)))

# make tab formatted entries for output file
allwords = ["{}\t{}".format(x[0], x[1]) for x in sorted_words]

# write output to file
with open(output_file, "w") as f:
    f.write("\n".join(allwords))
