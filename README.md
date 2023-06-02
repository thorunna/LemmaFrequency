# LemmaFrequency

Scripts for extracting information on lemmas in three Icelandic corpora: [The Icelandic Parsed Historical Corpus](https://clarin.is/en/resources/icepahc/) (IcePaHC), the [Tagged Icelandic Corpus](https://clarin.is/en/resources/mim/) (MÍM) and the [Icelandic Gigaword Corpus](http://igc.arnastofnun.is) (RMH).

The scripts are all stored in the [scripts](https://github.com/thorunna/LemmaFrequency/tree/main/scripts) directory, which is divided further into directories for each corpus. Two scripts are available for each corpus:

- '*corpus*_simple_freq.py' returns a tsv file containing a lemma, its word category, along with the gender if the word in question is a noun, and its frequency, in a descending order.
- '*corpus*_get_lemma_freq.py' returns a tsv file containing frequency information based on each sentence in the corpus. The information shown includes sentence IDs, text genre, the sentence text, and a frequency vector. Further information on the output, along with instructions on how to run the script, can be found in the script itself.

Some of the scripts' output files are stored under the [output](https://github.com/thorunna/LemmaFrequency/tree/main/output) directory, i.e. simple frequency files on IcePaHC and MÍM, along with the full frequency information on both corpora. The 'icepahc_full_freq.tsv' and 'mim_full_freq.tsv' files include frequency information on all three corpora, but the information from the Gigaword Corpus is currently only from a small subset of the corpus. This will be updated.