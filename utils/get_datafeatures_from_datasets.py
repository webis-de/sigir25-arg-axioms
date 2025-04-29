import os
from pyterrier.datasets import get_dataset
import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import settings as s
import pickle
import pandas as pd
from loguru import logger
import re


# clean human annotated qrels so no irrelevant judgments are in the dataset
def filter_out_irrelevant_qrels(df):

    indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
    index = pt.IndexFactory.of(indexref)
    meta = index.getMetaIndex()

    collect_docids  =  []
    for docno in df['docno']:
        docid = meta.getDocument('docno' , docno)
        if docid != -1:
            docno_index = meta.getItem("docno" , docid)
            assert docno == docno_index
        collect_docids.append(docid)
    df['docid'] = collect_docids

    df_merged_only_docs_in_index = df[df['docid'] != -1] # filter out docnos not in the index
    df_merged_only_docs_in_index = df_merged_only_docs_in_index.drop('docid', axis=1)

    print(f"Filtered out {len(df) - len(df_merged_only_docs_in_index)} documents that are not in the index")

    if len(df_merged_only_docs_in_index) == 0:
        logger.error(f"No documents in Index found")
        return None

    return df_merged_only_docs_in_index


def get_qrels_human_annotation():
    path_to_data_human_judgments = s.QRELS_SAVE_PATH / (s.DATASET_NAME_SHORT + '.pkl')
    os.makedirs(path_to_data_human_judgments.parent, exist_ok=True)

    if path_to_data_human_judgments.exists():
        with open(path_to_data_human_judgments , "rb") as pickle_file :
            data_qrels = pickle.load(pickle_file) # includes human knowledge

    else :
        dataset = get_dataset(f'irds:{s.DATASET}')
        data_qrels = dataset.get_qrels()
        data_qrels = filter_out_irrelevant_qrels(data_qrels) # remove docnos not in the index
        with open(path_to_data_human_judgments, "wb") as pickle_file :
            pickle.dump(data_qrels, pickle_file)

    return data_qrels


def get_qrels():

    data_qrels_human = get_qrels_human_annotation()
    data_qrels = data_qrels_human

    qrels = data_qrels[['qid','docno','label']].copy()
    qrels.loc[: , "label"] = qrels["label"].replace({-2 : 0})

    return qrels

def process_touche20(df):
    df['query'] = df['text'].str.lower().str.replace(r'[.?!]' , '' , regex=True)
    return df


def get_dataset_queries():
    path_to_data = s.QRELS_SAVE_PATH / 'data_topics' / (s.DATASET_NAME_SHORT + '.pkl')
    os.makedirs(path_to_data.parent, exist_ok=True)
    if path_to_data.exists() :
        with open(path_to_data , "rb") as pickle_file :
            loaded_data = pickle.load(pickle_file)
            return loaded_data[['qid','query']]

    dataset = get_dataset(f'irds:{s.DATASET}')
    queries = dataset.get_topics()

    if s.DATASET_NAME_SHORT == 'touche20': # do additional processing for Touche20
        queries = process_touche20(queries)

    with open(path_to_data , "wb") as pickle_file :
        pickle.dump(queries , pickle_file)
    return queries[['qid','query']]




