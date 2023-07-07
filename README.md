# LemmaFrequency

Scripts for extracting information on lemmas in three Icelandic corpora: [The Icelandic Parsed Historical Corpus](https://clarin.is/en/resources/icepahc/) (IcePaHC), the [Tagged Icelandic Corpus](https://clarin.is/en/resources/mim/) (MÍM) and the [Icelandic Gigaword Corpus](http://igc.arnastofnun.is) (IGC).

The scripts are all stored in the [scripts](https://github.com/thorunna/LemmaFrequency/tree/main/scripts) directory, which is divided further into directories for each corpus. Two scripts are available for each corpus:

- `_corpus_ _simple_freq.py` returns a tsv file containing a lemma, its word category, along with the gender if the word in question is a noun, and its frequency, in a descending order.
- `*corpus*_get_lemma_freq.py` returns a tsv file containing frequency information based on each sentence in the corpus. The information shown includes sentence IDs, text genre, the sentence text, and a frequency vector. Further information on the output, along with instructions on how to run the script, can be found in the script itself.

The scripts' output files are stored under the [output](https://github.com/thorunna/LemmaFrequency/tree/main/output) directory. Some files cannot be stored in the repository due to size limitations, so a download link is provided instead. A full frequency list for IGC cannot be provided in the repository due to computing limitations.

The simple frequency lists, compiled using `*corpus*_simple_freq.py`, are computed based on the frequency of a lemma, its word category, and the lemma's grammatical gender
if it is a noun. This results in more fine-grained results than merely counting the frequency of a lemma, independent of its word category and gender. Existing tags in IGC are used for this calculation, while IcePaHC and MÍM are tagged using [ABLTagger](https://github.com/steinst/ABLTagger), which uses the same tagset as is used in IGC. 
