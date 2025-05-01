# this model is designed to work on the annotated data
import pickle

import pyterrier as pt

if not pt.java.started() :
    pt.java.init()

import pyterrier as pt
from pyterrier.datasets import get_dataset

if not pt.java.started() :
    pt.java.init()
import settings as s


def get_used_dataset_from_index(dataset_name):

    print(f"Getting data for {dataset_name}")
    s.set_data_manually(dataset_name)
    dataset = get_dataset(f'irds:{s.DATASET}')
    queries = dataset.get_topics()
    data_qrels = dataset.get_qrels()

    indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
    index = pt.IndexFactory.of(indexref)
    meta = index.getMetaIndex()


    docnos_content_dict = {}

    # handle the documents, which are scored and in the index
    for docno in data_qrels['docno'].unique():
        docid = meta.getDocument('docno' , docno)
        if docid != -1 :
            # extra check that the document is in the index
            docno_index = meta.getItem("docno", docid)
            assert docno == docno_index
            content = meta.getItem("text", docid)
            docnos_content_dict.update({docno : content})

    final_data_dict = {
        "queries" : queries,
        "data_qrels" : data_qrels,
        "docnos" : docnos_content_dict
    }

    with open(s.PATH_TOUCHE_21_FROM_INDEX_PKL_DATA, 'wb') as file :
        pickle.dump(final_data_dict, file)

if __name__ == '__main__' :
    touche_21_data = get_used_dataset_from_index('touche21')
