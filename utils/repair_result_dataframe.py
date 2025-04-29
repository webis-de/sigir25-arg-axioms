import sys

from utils.get_datafeatures_from_datasets import get_qrels,get_dataset_queries
import pandas as pd
import pickle
from pathlib import Path
import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import settings as s
from loguru import logger

# repair a Touche run, by deleting entries that are not in the index
def repair_touche_run(df):
    queries_df = get_dataset_queries()

    df_merged = pd.merge(df, queries_df, on='qid')

    indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
    index = pt.IndexFactory.of(indexref)
    meta = index.getMetaIndex()

    collect_docids  =  []
    for docno in df_merged['docno']:
        docid = meta.getDocument('docno' , docno)
        if docid != -1:
            # extra check that the document is in the index
            docno_index = meta.getItem("docno" , docid)
            assert docno == docno_index
        collect_docids.append(docid)
    df_merged['docid'] = collect_docids

    df_merged_only_docs_in_index = df_merged[df_merged['docid'] != -1] # filter out invalid docnos

    if len(df_merged_only_docs_in_index) == 0:
        logger.error(f"No documents in Index found")
        return None

    diff = len(df_merged) - len(df_merged_only_docs_in_index)
    logger.info(f"Number of documents filtered out from Touche Run {diff}")
    qids = df_merged_only_docs_in_index['qid'].unique()
    sub_frames = []
    for x in qids :
        repaired = rank_repair_single_qid(df_merged_only_docs_in_index, x)
        sub_frames.append(repaired)
    dataframe_participant = pd.concat(sub_frames)

    return dataframe_participant[['qid','docid', 'docno','rank','score','query']]


# trim the retrieval results to the top n, used if the qrels are not complete and need to be calculated
def cut_retrieval_results_top_n(df,cut_off=20,return_cut=False): # if not all documents can be provided a cut is brought back nontheless
    df = df.copy()
    df_filtered = df[(df['rank'] >= 0) & (df['rank'] < (cut_off))]

    qid_to_cut_off = []

    # go through the qids and check if each qid has the cut off number
    qids = df_filtered['qid'].unique()
    for qid in qids:
        df_qid = df_filtered[df_filtered['qid'] == qid]
        if len(df_qid) != cut_off:
            qid_to_cut_off.append(qid)

    if len(qid_to_cut_off) > 0 and return_cut == False:
        logger.error(f"Error in cut off, not all documents are in the top {cut_off} for qid {qid}")
        return None
    if len(qid_to_cut_off) > 0:
        df_filtered = df_filtered[~df_filtered['qid'].isin(qid_to_cut_off)]

    num_qids = df_filtered['qid'].nunique()
    print("Number of unique qids:", num_qids)
    return df_filtered

# repair missing, ranks, caused through filtering
def rank_repair_single_qid(df, qid_to_update):
    df = df.copy()
    df_qid = df[df['qid'] == qid_to_update]
    df_qid_sorted = df_qid.sort_values(by=['rank', 'score'], ascending=[True, False]).reset_index(drop=True)
    df_qid_sorted['rank'] = df_qid_sorted.index
    return df_qid_sorted

def repair_rank_retrieval_results_dataframe_drop_missing(df):
    docnos_qrels = get_qrels()[['qid', 'docno']]
    df = df.copy()

    number_rows_before = len(df)

    df_filtered = df.merge(docnos_qrels , on=['qid' , 'docno'] , how='left' , indicator=True)
    df_filtered = df_filtered[df_filtered['_merge'] == 'both'].drop(columns=['_merge']) # only keep results, for which judgments exist

    number_after = len(df_filtered)
    logger.info(f"Filtered out {number_rows_before - number_after} documents that are not in the qrels")

    # do repair on the underlying ranks
    qids = df_filtered['qid'].unique()
    sub_frames = []
    for x in qids:
        repaired = rank_repair_single_qid(df_filtered, x)
        sub_frames.append(repaired)
    return pd.concat(sub_frames)

