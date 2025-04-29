import pyterrier as pt

if not pt.java.started() :
    pt.java.init()

import string

import pandas as pd
from tabulate import tabulate

import settings as s


def calculate_values(data):

    print(len(data))
    data = pd.DataFrame(data)

    quantile_interpolation = "linear"

    data_mean = data.mean()
    data_05 = data.quantile(0.05)
    data_25 = data.quantile(0.25)
    data_median = data.quantile(0.5)
    data_75 = data.quantile(0.75)
    data_95 = data.quantile(0.95)
    data_max = data.max()
    data_min = data.min()
    data_std = data.std()

    # names for included columns
    cols_dict = [
            ("Mean", data_mean[0]),
            ("05 Perc.", data_05[0]),
            ("25 Perc.", data_25[0]),
            ("Median", data_median[0]),
            ("75 Perc.", data_75[0]),
            ("95 Perc.", data_95[0]),
            ("Max", data_max[0]),
            ("Min", data_min[0]),
            ("Std.", data_std[0]) ]
    return cols_dict

if __name__ == "__main__":
        s.set_data_manually('touche21')
        indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
        index = pt.IndexFactory.of(indexref)

        iter = index.get_corpus_iter()
        for x in iter:
            if x['docno'] == 'S9c060533-Ab2574a02':
                print(x)

        meta = index.getMetaIndex()

        # Retrieve all documents from the index
        for docno in range(0,10) :
            dat = meta.getDocument('docno', str(docno))

        doc = index.get_document(docid)
        print(doc)
        interesting_fields = 'S9c060533-Ab2574a02'
        calculate_values([1,2,3])
        total_length = []

        for x in generate_filter_qrels():
            premise = x["premises_texts"]
            translator = str.maketrans("", "", string.punctuation)
            clean_sentence = premise.lower().translate(translator)
            words = clean_sentence.split()
            words_nbr = len(words)
            total_length.append(words_nbr)

        res = calculate_values(total_length)
        x = tabulate(res,tablefmt="latex_raw", headers=["Metric", "Nbr. of Words"])
        print(x)

