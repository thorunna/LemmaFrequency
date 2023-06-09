"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the IcePaHC corpus. The output is twofold:

add_freq_V2() reads an input file which consists of sentence IDs in the corpus, and returns frequency information
on lemmas in that sentence. The added output shows the following information, separated by a colon:

    Tuple containing the lemma, its word category (along with its grammatical gender if the lemma in question is a noun) and the lemmas frequency.
    A frequency vector, showing each lemma's frequency in the order which the lemma appears in the corpus.

compile_full_freq() returns frequency information for each sentence in the corpus. The information shown is the following, 
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
    in IcePaHC, the MÍM corpus and the Gigaword Corpus.
    A frequency vector, showing each lemma's frequency in IcePaHC, the MÍM corpus and the Gigaword Corpus, in the order in which the lemma appears in the corpus.

"""

import json
import requests
from collections import Counter
from collections import OrderedDict
import os
import string
import glob
import xml.etree.ElementTree
import csv

basedir = "/Users/torunnarnardottir/Vinna/icepahc-v0.9/txt/"
file_list = sorted(os.listdir(basedir))
input_file_V2 = "/Users/torunnarnardottir/Vinna/icepahc-v0.9/infoTheoryTestV2.ice.treeIDandIDfixed.cod.ooo"

mim_basedir = "/Users/torunnarnardottir/Vinna/MIM/"
mim_file_list = "{}fileList.txt".format(mim_basedir)
giga_file_list = [
    os.path.abspath(filename)
    for filename in glob.glob(
        "/Users/torunnarnardottir/Vinna/rmh/**/*.xml", recursive=True
    )
]

output_file_total = (
    "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/icepahc_full_freq.tsv"
)


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


def clean_tagged_output(tagged_text, token_list, sent_id, delimiter):
    """
    Filter out relevant data from the tagging and lemmatizing step
    """
    token_list[sent_id] = []
    for paragraph in tagged_text.values():
        for sentences in paragraph:
            sentences = dict(sentences)
        # Looping through tagged output to get to words
        for sentence in sentences.values():
            for sent in sentence:
                for word in sent:
                    if word["word"] not in string.punctuation:
                        token = word["word"]
                        tag = word["tag"]
                        lemma = word["lemma"]
                        # if noun, include gender with tag
                        if tag[0] == "n":
                            tag = tag[:2]
                        else:
                            tag = tag[0]

                        token_list[sent_id].append((token, tag, lemma))

                        yield "{}{}{}".format(lemma, delimiter, tag)


# XML namespace
ns = {"tei": "http://www.tei-c.org/ns/1.0"}


def mim_text_words(teifile):
    """
    Function to extract lemma occurences from tei xml file in the MÍM corpus
    """
    root = xml.etree.ElementTree.parse(teifile).getroot()
    for sent in root.findall(".//tei:s", ns):
        for aword in sent:
            if aword.get("type") != "punctuation":
                lemma = aword.get("lemma")
                tag = aword.get("type")

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

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

                # if noun, include gender with tag
                if tag[0] == "n":
                    tag = tag[:2]
                else:
                    tag = tag[0]

                yield "{}{}{}".format(lemma, ", ", tag)


def add_freq_V2(output_file_V2):
    """
    Function for adding lemma frequencies for each sentence in an existing infoTheoryTestV2 file
    """
    c = Counter()
    token_list = dict()

    for file in file_list:
        print("Compiling frequency information from {}...".format(file))
        psd_path = (
            "/".join(basedir.split("/")[:-2])
            + "/psd/"
            + ".".join(file.split(".")[:-1])
            + ".psd"
        )
        ids = []
        # Reading .psd version of file to get sentence IDs
        with open(psd_path, "r", encoding="utf-8") as psd_file:
            for line in psd_file:
                if line.strip(" ").startswith("(ID"):
                    psd_id = line.split(",")[-1].split(")")[0]
                    if psd_id.startswith("."):
                        psd_id = psd_id.split(".")[1]
                    ids.append(psd_id)
            # Most .psd files are missing the final ID
            if "." in psd_id:
                psd_id = psd_id.split(".")[1]
                ids.append(str(int(psd_id) + 1))
                ids.append(str(int(psd_id) + 2))
                ids.append(str(int(psd_id) + 3))
                ids.append(str(int(psd_id) + 4))
                ids.append(str(int(psd_id) + 5))
                ids.append(str(int(psd_id) + 6))
                ids.append(str(int(psd_id) + 7))
            else:
                ids.append(str(int(psd_id) + 1))
                ids.append(str(int(psd_id) + 2))
                ids.append(str(int(psd_id) + 3))
                ids.append(str(int(psd_id) + 4))
                ids.append(str(int(psd_id) + 5))
                ids.append(str(int(psd_id) + 6))
                ids.append(str(int(psd_id) + 7))
        full_path = basedir + file
        file = file.split(".")[1]
        with open(full_path, "r", encoding="utf-8") as input_file:
            sent_count = 0
            for line in input_file:
                t = tag_and_lemmatize(line)
                sent_id = file.lower() + "." + str(ids[sent_count])
                c.update(clean_tagged_output(t, token_list, sent_id, ", "))
                sent_count += 1

    output_file_V2 = open(output_file_V2, "w")

    with open(
        input_file_V2,
        "r+",
    ) as input_file:
        for line in input_file:
            sent_id = ".".join(line.rstrip("\n").split(":")[-2:]).lower()
            # Some extra lines are present in input file
            if sent_id == "z.xxxgenre@":
                continue
            # Errors in input file handled, e.g. nar@1450.bandamenn.nar-sag,26.11.
            # The file and sent ID is usually shown differently, e.g. viglundur:1286
            elif "@" in sent_id:
                begin = sent_id.split(".")[2]
                end = sent_id.split(",")[1]
                if end.startswith("."):
                    sent_id = begin + end
                else:
                    sent_id = begin + "." + end
            output_file_V2.write(line.rstrip("\n"))
            output_file_V2.write(":")
            for word in token_list[sent_id]:
                lemma_tuple = str(word[2]) + ", " + str(word[1])
                output_tuple = (lemma_tuple, c[lemma_tuple])
                output_file_V2.write(str(output_tuple))
                output_file_V2.write(" ")
            output_file_V2.write(":")
            for word in token_list[sent_id]:
                lemma_tuple = str(word[2]) + ", " + str(word[1])
                output_file_V2.write(str(c[lemma_tuple]))
                output_file_V2.write(" ")
            output_file_V2.write("\n")

    output_file_V2.close()


def compile_full_freq(output_file_total):
    """
    Function for compiling frequency information from IcePaHC files and returning it in a file in the following format:
    testID\tsentenceID\tSentence number in text\tSentence text\tTuple with each word's lemma, tag and frequency\tFrequency vector
    """
    c = Counter()
    mim_c = Counter()
    giga_c = Counter()
    token_list = OrderedDict()
    text_list = dict()

    output_file = open(output_file_total, "w")

    with open(mim_file_list) as f:
        print("Compiling frequency information from the MÍM corpus...")
        reader = csv.DictReader(f, delimiter="\t")
        for text_count, item in enumerate(reader):
            folder = item["Folder"]
            fname = item["File Name"]
            full_fname = "{}{}/{}".format(mim_basedir, folder, fname)
            mim_c.update(mim_text_words(full_fname))

    print("Compiling frequency information from the Gigaword Corpus...")
    # compile frequency information from the Gigaword Corpus
    for file in sorted(giga_file_list):
        with open(file, "r"):
            giga_c.update(giga_text_words(file))

    print("Compiling frequency information from IcePaHC...")
    for file in file_list:
        psd_path = (
            "/".join(basedir.split("/")[:-2])
            + "/psd/"
            + ".".join(file.split(".")[:-1])
            + ".psd"
        )

        ids = []
        with open(psd_path, "r", encoding="utf-8") as psd_file:
            for line in psd_file:
                if line.strip(" ").startswith("(ID"):
                    psd_id = line.split(",")[-1].split(")")[0]
                    if psd_id.startswith("."):
                        psd_id = psd_id.split(".")[1]
                    ids.append(psd_id)
            # Most .psd files are missing the final ID or multiple final IDs
            if "." in psd_id:
                psd_id = psd_id.split(".")[1]
                ids.append(str(int(psd_id) + 1))
                ids.append(str(int(psd_id) + 2))
                ids.append(str(int(psd_id) + 3))
                ids.append(str(int(psd_id) + 4))
                ids.append(str(int(psd_id) + 5))
                ids.append(str(int(psd_id) + 6))
                ids.append(str(int(psd_id) + 7))
            else:
                ids.append(str(int(psd_id) + 1))
                ids.append(str(int(psd_id) + 2))
                ids.append(str(int(psd_id) + 3))
                ids.append(str(int(psd_id) + 4))
                ids.append(str(int(psd_id) + 5))
                ids.append(str(int(psd_id) + 6))
                ids.append(str(int(psd_id) + 7))
        full_path = basedir + file
        file_simple = file.split(".")[1]
        with open(full_path, "r", encoding="utf-8") as input_file:
            sent_count = 0
            for line in input_file:
                t = tag_and_lemmatize(line)
                sent_id = file_simple.lower() + "." + str(ids[sent_count])
                text_list[sent_id] = line.rstrip("\n")
                c.update(clean_tagged_output(t, token_list, sent_id, ", "))
                sent_count += 1

        text_id = file
        info_file = (
            "/".join(basedir.split("/")[:-2])
            + "/info/"
            + ".".join(file.split(".")[:-1])
            + ".info"
        )
        with open(info_file, "r") as info_file:
            for line in info_file:
                if line.startswith("Birthdate:"):
                    author_year = line.split("\t")[-1].rstrip()
                elif line.startswith("Date"):
                    # tab is usually used to indicate the date, but several spaces are used in one case
                    try:
                        year = line.split("\t")[-1].rstrip()
                    except IndexError:
                        year = ""
                elif line.startswith("Genre"):
                    genre = line.split("\t")[-1].rstrip()
            author_sex = ""

        full_path = basedir + file
        file = file.split(".")[1]
        with open(full_path, "r") as input_file:
            sent_count = 0
            for line in input_file:
                sent_id = file.lower() + "." + str(ids[sent_count])

                tup = []
                vector = []
                for word in token_list[sent_id]:
                    lemma_tuple = str(word[2]) + ", " + str(word[1])
                    output_tuple = (
                        lemma_tuple,
                        c[lemma_tuple],
                        mim_c[lemma_tuple],
                        giga_c[lemma_tuple],
                    )
                    tup.append(str(output_tuple))
                    vector.append(
                        str((c[lemma_tuple], mim_c[lemma_tuple], giga_c[lemma_tuple]))
                    )
                output = [
                    text_id,
                    sent_id,
                    sent_id.split(".")[1],
                    genre,
                    year,
                    author_year,
                    author_sex,
                    text_list[sent_id],
                    " ".join(tup),
                    " ".join(vector),
                ]
                output_file.write("\t".join(output))
                output_file.write("\n")

                sent_count += 1

    output_file.close()


compile_full_freq(output_file_total)
