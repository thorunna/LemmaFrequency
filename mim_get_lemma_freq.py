"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the MÍM corpus. 

compile_full_frequency() returns frequency information for each sentence in the corpus. The information shown is the following, 
separated by a tab:

    The text ID
    The sentence ID (includes the text ID)
    The sentence's number in the text
    The sentence's text
    A tuple containing the lemma, its word category (along with its grammatical gender if the lemma in question is a noun) and the lemma's frequency.
    A frequency vector, showing each lemma's frequency in the order in which the lemma appears in the corpus.

"""

import xml.etree.ElementTree
from collections import Counter
import csv
import sys

basedir = "/Users/torunnarnardottir/Vinna/MIM/"
file_list = "{}fileList.txt".format(basedir)
output_file = "/Users/torunnarnardottir/Vinna/MIM/allfreq_sents.tsv"


# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}

# function to extract lemma occurences from tei xml file
def text_words(teifile, token_list, text_list):
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        sent_no = sent.get("n")
        token_list[sent_no] = []
        text_list[sent_no] = []
        for aword in sent:
            text_list[sent_no].append(aword.text)
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("type")

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

                token_list[sent_no].append((tag, lemma))

                yield "{}{}{}".format(lemma, ", ", tag)


def compile_full_frequency(output_file):
    """
    Function for compiling frequency information from MIM files and returning it in a file in the following format:
    testID\tsentenceID\tSentence number in text\tSentence text\tTuple with each word's lemma, tag and frequency\tFrequency vector
    """
    # counter object that updates frequencies for lemmas file by file
    c = Counter()
    token_list = dict()
    text_list = dict()

    with open(output_file, "w") as output_file:
        with open(file_list) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for text_count, item in enumerate(reader):
                folder = item["Folder"]
                fname = item["File Name"]
                full_fname = "{}{}/{}".format(basedir, folder, fname)
                # update counter with words from the current text
                c.update((text_words(full_fname, token_list, text_list)))
                sys.stdout.write("\rTexts processed: {}".format(text_count))

            for sent_id in token_list:
                tup = []
                vector = []
                for word in token_list[sent_id]:
                    lemma_tuple = str(word[1]) + ", " + str(word[0])
                    output_tuple = (lemma_tuple, c[lemma_tuple])
                    tup.append(str(output_tuple))
                    vector.append(str(c[lemma_tuple]))
                output = [
                    fname,
                    fname.split(".")[0] + "." + sent_id,
                    sent_id,
                    " ".join(text_list[sent_id]),
                    " ".join(tup),
                    " ".join(vector),
                ]
                output_file.write("\t".join(output))
                output_file.write("\n")
