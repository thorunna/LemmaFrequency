"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the MÍM corpus. 

compile_full_frequency() returns frequency information for each sentence in the corpus. The information shown is the following, 
separated by a tab:

    The text ID
    The sentence ID (includes the text ID)
    The sentence's number in the text
    The text's genre
    Date of publication
    The author's birth year, if available
    The author's sex, if available
    The sentence's text
    A tuple containing the lemma, its word category (along with its grammatical gender if the lemma in question is a noun) and the lemma's frequency
    in the MÍM corpus, IcePaHC and the Gigaword Corpus.
    A frequency vector, showing each lemma's frequency in the MÍM corpus, IcePaHC and the Gigaword Corpus, in the order in which the lemma appears in the corpus.

"""

import xml.etree.ElementTree
from collections import Counter
import csv
import sys
import os
import glob
import json
import requests
import string

basedir = "/Users/torunnarnardottir/Vinna/MIM/"
file_list = "{}fileList.txt".format(basedir)

icepahc_file_list = [
    os.path.abspath(filename)
    for filename in glob.iglob("/Users/torunnarnardottir/Vinna/icepahc-v0.9/**")
]
rmh_file_list = [
    os.path.abspath(filename)
    for filename in glob.iglob("/Users/torunnarnardottir/Vinna/rmh/**")
]

output_file = "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/mim_full_freq.tsv"


# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}


def text_words(teifile, token_list, text_list):
    """
    Function to extract lemma occurences from tei xml file in the MÍM corpus
    """
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


def rmh_text_words(teifile):
    """
    Function to extract lemma occurences from tei xml file in the Gigaword Corpus
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        for aword in sent:
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("pos")

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

                yield "{}{}{}".format(lemma, ", ", tag)


def tag_and_lemmatize(text):
    """
    Calls tagging API from http://malvinnsla.arnastofnun.is/about_en
    """
    url = "http://malvinnsla.arnastofnun.is"
    payload = {"text": text, "lemma": "on"}
    headers = {}
    try:
        res = requests.post(url, data=payload, headers=headers)
        tagged = json.loads(res.text)
    except ConnectionError as exception:
        print(exception)
        print("\n\n")
    return tagged


def clean_tagged_output(tagged_text, delimiter):
    """
    Filter out relevant data from the tagging and lemmatizing step
    """
    for paragraph in tagged_text.values():
        for sentences in paragraph:
            sentences = dict(sentences)
        # Looping through tagged output to get to words
        for sentence in sentences.values():
            for sent in sentence:
                for word in sent:
                    if word["word"] not in string.punctuation:
                        tag = word["tag"]
                        lemma = word["lemma"]
                        # if noun, include gender with tag
                        if tag[0] == "n":
                            tag = tag[:2]
                        else:
                            tag = tag[0]

                        yield "{}{}{}".format(lemma, delimiter, tag)


def compile_full_frequency(output_file):
    """
    Function for compiling frequency information from MIM files and returning it in a file in the following format:
    testID\tsentenceID\tSentence number in text\tSentence text\tTuple with each word's lemma, tag and frequency\tFrequency vector
    """
    # counter object that updates frequencies for lemmas file by file
    c = Counter()
    icepahc_c = Counter()
    rmh_c = Counter()
    token_list = dict()
    text_list = dict()

    with open(output_file, "w") as output_file:
        print("Compiling frequency information from IcePaHC...")
        # compile frequency information from IcePaHC
        for file in icepahc_file_list:
            with open(file, "r") as input_file:
                for line in input_file:
                    t = tag_and_lemmatize(line)
                    icepahc_c.update(clean_tagged_output(t, ", "))
        print("Compiling frequency information from the Gigaword Corpus...")
        # compile frequency information from the Gigaword Corpus
        for file in sorted(rmh_file_list):
            with open(file, "r"):
                rmh_c.update(rmh_text_words(file))
        with open(file_list) as f:
            print("Compiling frequency information from the MÍM corpus...")
            reader = csv.DictReader(f, delimiter="\t")
            for text_count, item in enumerate(reader):
                folder = item["Folder"]
                fname = item["File Name"]
                full_fname = "{}{}/{}".format(basedir, folder, fname)
                # update counter with words from the current text
                c.update((text_words(full_fname, token_list, text_list)))
                sys.stdout.write("\rTexts processed: {}".format(text_count))

                genre = folder
                year = item["Date"]
                author_year = ""
                author_sex = ""

            for sent_id in token_list:
                tup = []
                vector = []
                for word in token_list[sent_id]:
                    lemma_tuple = str(word[1]) + ", " + str(word[0])
                    output_tuple = (
                        lemma_tuple,
                        c[lemma_tuple],
                        icepahc_c[lemma_tuple],
                        rmh_c[lemma_tuple],
                    )
                    tup.append(str(output_tuple))
                    vector.append(
                        str(
                            (
                                c[lemma_tuple],
                                icepahc_c[lemma_tuple],
                                rmh_c[lemma_tuple],
                            )
                        )
                    )
                output = [
                    fname,
                    fname.split(".")[0] + "." + sent_id,
                    sent_id,
                    genre,
                    year,
                    author_year,
                    author_sex,
                    " ".join(text_list[sent_id]),
                    " ".join(tup),
                    " ".join(vector),
                ]
                output_file.write("\t".join(output))
                output_file.write("\n")


compile_full_frequency(output_file)
