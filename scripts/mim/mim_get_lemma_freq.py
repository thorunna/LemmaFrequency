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
    for filename in glob.iglob("/Users/torunnarnardottir/Vinna/icepahc-v0.9/txt/**")
]
giga_file_list = [
    os.path.abspath(filename)
    for filename in glob.glob(
        "/Users/torunnarnardottir/Vinna/rmh/**/*.xml", recursive=True
    )
]

output_file = "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/mim_full_freq.tsv"


# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}


def text_words(teifile, genre, year, author_year, author_sex, token_list, text_list):
    """
    Function to extract lemma occurences from tei xml file in the MÍM corpus
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        sent_info = ":".join(
            [teifile, sent.get("n"), genre, year, author_year, author_sex]
        )
        token_list[sent_info] = []
        text_list[sent_info] = []
        for aword in sent:
            text_list[sent_info].append(aword.text)
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("type")

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

                token_list[sent_info].append((tag, lemma))

                yield "{}{}{}".format(lemma, ", ", tag)


def giga_text_words(teifile):
    """
    Function to extract lemma occurences from tei xml file in the Gigaword Corpus
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        for aword in sent:
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("pos")

                if lemma is not None and tag is not None:

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
    giga_c = Counter()
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
        for file in sorted(giga_file_list):
            with open(file, "r"):
                giga_c.update(giga_text_words(file))
        with open(file_list) as f:
            print("Compiling frequency information from the MÍM corpus...")
            reader = csv.DictReader(f, delimiter="\t")
            for text_count, item in enumerate(reader):
                folder = item["Folder"]
                fname = item["File Name"]
                full_fname = "{}{}/{}".format(basedir, folder, fname)
                year = item["Date"]
                author_year = ""
                author_sex = ""
                # update counter with words from the current text
                c.update(
                    (
                        text_words(
                            full_fname,
                            folder,
                            year,
                            author_year,
                            author_sex,
                            token_list,
                            text_list,
                        )
                    )
                )

            for sent_info in token_list:
                text_id = "/".join(sent_info.split(":")[0].split("/")[-2:])
                sent_id = ".".join(
                    [
                        "/".join(text_id.split("/")[-2:]).split(".")[0],
                        sent_info.split(":")[1],
                    ]
                )
                sent_no = sent_info.split(":")[1]
                genre = sent_info.split(":")[2]
                year = sent_info.split(":")[3]
                author_year = sent_info.split(":")[4]
                author_sex = sent_info.split(":")[5]
                tup = []
                vector = []
                for word in token_list[sent_info]:
                    lemma_tuple = str(word[1]) + ", " + str(word[0])
                    output_tuple = (
                        lemma_tuple,
                        c[lemma_tuple],
                        icepahc_c[lemma_tuple],
                        giga_c[lemma_tuple],
                    )
                    tup.append(str(output_tuple))
                    vector.append(
                        str(
                            (
                                c[lemma_tuple],
                                icepahc_c[lemma_tuple],
                                giga_c[lemma_tuple],
                            )
                        )
                    )
                output = [
                    text_id,
                    sent_id,
                    sent_no,
                    genre,
                    year,
                    author_year,
                    author_sex,
                    " ".join(text_list[sent_info]),
                    " ".join(tup),
                    " ".join(vector),
                ]
                output_file.write("\t".join(output))
                output_file.write("\n")


compile_full_frequency(output_file)
