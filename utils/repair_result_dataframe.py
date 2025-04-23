import sys

from utils.get_datafeatures_from_datasets import get_qrels,get_dataset_queries,update_dataset_llm_qrels
from llm_prompting_qrels.llm_control import query_llm
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

    indexref = pt.IndexRef.of(str(s.dataset_index_dir))
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
    # check the cutout is sequential
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

def adjust_retrieval_results_dataframe_drop_missing(df):
    docnos_qrels = get_qrels(just_human_qrels=True)[['qid', 'docno']]
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

def update_dataset_llm_qrels_helper(data_llm):
    relevance = data_llm['relevance_llm']
    quality = data_llm['quality_llm']
    docno = data_llm['docno']
    qid = data_llm['qid']

    if (relevance is None) or (quality is None):
        logger.error(f"Document {docno} has no relevance or quality")
        sys.exit(1)
    if relevance not in [-2,0,1,2]:
        logger.error(f"Document {docno} has invalid relevance {relevance}")
        sys.exit(1)
    if quality not in [0,1,2]:
        logger.error(f"Document {docno} has invalid quality {quality}")
        sys.exit(1)

    update_dataset_llm_qrels(data_llm)
    logger.info(f"Annotated document {docno} with relevance {relevance} and quality {quality}")

def log_qrel_combinations_not_included_in_original_qrels(df_to_check, experiment_name):
    human_qrels = get_qrels(just_human_qrels=True, ignore_qrels_to_use=True)
    df_combined = pd.merge(df_to_check , human_qrels , on=['qid' , 'docno'] , how='left' , indicator=True) # merge in order to determine if documents exist without qrels
    df_unique_to_df1 = df_combined[df_combined['_merge'] == 'left_only']

    path_to_write_missing = s.ADDITIONAL_QREL_LOCATION / s.dataset_name_short / (experiment_name + s.ADDITIONAL_QREL_FILE_ENDING)
    Path(path_to_write_missing).parent.mkdir(parents=True, exist_ok=True)
    with open(path_to_write_missing, 'wb') as f:
        pickle.dump(df_unique_to_df1, f)

def adjust_retrieval_results_dataframe_repair_get_missing(df):
    df = df.copy()
    qrel_df = get_qrels(ignore_qrels_to_use=True)
    queries = get_dataset_queries()
    # docnos_qrels = qrel_df['docno'].values

    df_combined = pd.merge(df , qrel_df , on=['qid' , 'docno'] , how='left' , indicator=True) # merge in order to determine if documents exist without qrels
    df_unique_to_df1 = df_combined[df_combined['_merge'] == 'left_only']

    indexref = pt.IndexRef.of(str(s.dataset_index_dir))
    index = pt.IndexFactory.of(indexref)
    # inv = index.getInvertedIndex()
    meta = index.getMetaIndex()
    logger.info(f"Number of documents not annotated {len(df_unique_to_df1)}")

    if len(df_unique_to_df1) == 0 :
        return
    if s.LLM_ANNOTATION == False:
        logger.error("LLM Annotation is disabled")
        sys.exit(1)

    data_all_instances_to_annotate = []

    for i,x in df_unique_to_df1.iterrows():
        docid = x['docid']
        qid = x['qid']
        docno = x['docno']
        index_docno = meta.getItem("docno" , docid)
        assert docno == index_docno

        document = meta.getItem("text" , docid)
        title = meta.getItem("title" , docid)

        topic = queries[queries['qid'] == qid]['query'].values[0]

        data_llm_dict = {'topic' : topic , 'document' : document,'title' : title, 'docno' : docno, 'qid' : qid}
        data_all_instances_to_annotate.append(data_llm_dict)

        for data_llm_dict in data_all_instances_to_annotate:
            data_llm = query_llm(data_llm_dict)
            update_dataset_llm_qrels_helper(data_llm)


# adjust qrels, which are considered for the evaluation
def set_retrieval_results_qrels_top_n(dataframes):
    considered_documents = []
    if not isinstance(dataframes, list):
        dataframes = [dataframes]
    for df in dataframes:
        filtered_df_relevance = df[['qid','docno']]
        considered_documents.append(filtered_df_relevance)

    all_relevant_df = pd.concat(considered_documents)
    all_relevant_df = all_relevant_df.drop_duplicates()
    qrel_df_human = get_qrels(just_human_qrels=True, ignore_qrels_to_use=True)
    qrel_df = get_qrels(ignore_qrels_to_use=True)

    filtered_df = qrel_df.merge(all_relevant_df, on=['qid', 'docno'], how='left', indicator=True)
    filtered_df = filtered_df[filtered_df['_merge'] == 'both'].drop(columns=['_merge'])
    assert len(filtered_df) == len(all_relevant_df)
    assert filtered_df.shape != all_relevant_df.shape

    # merged_df_test = filtered_df.merge(qrel_df_human, how='inner')

    merged_df = pd.concat([filtered_df, qrel_df_human])
    merged_df = merged_df.drop_duplicates()

    s.QRELS_TO_USE_DF = merged_df
