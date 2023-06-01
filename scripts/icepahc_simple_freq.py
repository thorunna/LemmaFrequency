"""
Þórunn Arnardóttir (thar@hi.is)

Script for extracting frequency information on lemmas in the IcePaHC corpus. The output is a .tsv file containing
the following information:

    Lemma
    Word category, including the gender if the lemma in question is a noun
    The lemma's frequency

"""

import json
import requests
from collections import Counter
import os
import string
import operator

# Directory where IcePaHC is stored.
basedir = "/Users/torunnarnardottir/Vinna/icepahc-v0.9/txt/"
file_list = sorted(os.listdir(basedir))

# Path of output file
output_file = (
    "/Users/torunnarnardottir/Vinna/LemmaFrequency/output/icepahc_simple_freq.tsv"
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


def clean_tagged_output(tagged_text):
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

                        yield "{}{}{}".format(lemma, "\t", tag)


# counter object that updates frequencies for lemmas file by file
c = Counter()

for file in file_list:
    full_path = basedir + file
    file_simple = file.split(".")[1]
    # display progress
    print("Processing {}...".format(file))

    with open(full_path, "r", encoding="utf-8") as input_file:
        for line in input_file:
            t = tag_and_lemmatize(line)
            c.update(clean_tagged_output(t))

# sort frequency list in reverse order by counts (most frequent first)
sorted_words = reversed(sorted(c.items(), key=operator.itemgetter(1)))

# make tab formatted entries for output file
allwords = ["{}\t{}".format(x[0], x[1]) for x in sorted_words]

# write output to file
with open(output_file, "w") as f:
    f.write("\n".join(allwords))
