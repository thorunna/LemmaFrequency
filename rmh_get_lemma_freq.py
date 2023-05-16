"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the Icelandic Gigaword corpus. The script expects a directory which
only includes directories with relevant XML files.

compile_full_frequency() returns frequency information for each sentence in the corpus. The information shown is the following, 
separated by a tab:

    The text ID
    The sentence ID (includes the text ID)
    The sentence's number in the text
    The sentence's text
    A tuple containing the lemma, its word category (along with its grammatical gender if the lemma in question is a noun) and the lemma's frequency.
    A frequency vector, showing each lemma's frequency in the order in which the lemma appears in the corpus.

"""

from collections import Counter
import xml.etree.ElementTree
import csv
import sys
import operator
import time
import os
import glob

# Directory where The Gigaword Corpus is stored.
basedir = "/Users/torunnarnardottir/Vinna/rmh"
file_list = [
    os.path.abspath(filename)
    for filename in glob.iglob(
        "/Users/torunnarnardottir/Vinna/rmh/**",
        recursive=True,
    )
    if filename.endswith(".xml")
]
output_file = "/Users/torunnarnardottir/Vinna/rmh/rmh_full_freq.tsv"

# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}

global total_word_count
total_word_count = 0

# function to extract lemma occurences from tei xml file
def text_words(teifile, token_list, text_list):
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        sent_no = ".".join(
            sent.get("{http://www.w3.org/XML/1998/namespace}id").split(".")[-2:]
        )
        token_list[sent_no] = []
        text_list[sent_no] = []
        for aword in sent:
            text_list[sent_no].append(aword.text)
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("pos")

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

                token_list[sent_no].append((tag, lemma))

                yield "{}{}{}".format(lemma, ", ", tag)


def compile_full_frequency(output_file):
    c = Counter()
    token_list = dict()
    text_list = dict()

    out = open(output_file, "w")

    for file in sorted(file_list):
        print("Compiling frequency information from {}...".format(file))
        text_count = 1
        with open(file, "r"):
            text_id = file.split("/")[-1]
            c.update((text_words(file, token_list, text_list)))

            for sent_id in token_list:
                tup = []
                vector = []
                for word in token_list[sent_id]:
                    lemma_tuple = str(word[1]) + ", " + str(word[0])
                    output_tuple = (lemma_tuple, c[lemma_tuple])
                    tup.append(str(output_tuple))
                    vector.append(str(c[lemma_tuple]))
                output = [
                    text_id,
                    text_id.split(".")[0] + "." + sent_id,
                    sent_id,
                    " ".join(text_list[sent_id]),
                    " ".join(tup),
                    " ".join(vector),
                ]
                out.write("\t".join(output))
                out.write("\n")

            text_count += 1

    out.close()


compile_full_frequency(output_file)
