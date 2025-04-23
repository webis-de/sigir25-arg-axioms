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

location_storage = s.PROJECT_ROOT / '_storage'

# clean human annotated qrels so no irrelevant judgments are in the dataset
def filter_out_irrelevant_qrels(df):

    indexref = pt.IndexRef.of(str(s.dataset_index_dir))
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

def get_qrels_llm_annotation():
    path_to_data_llm_judgments = location_storage / 'data_qrels' / (s.dataset_name_short + '_llm_annotation.pkl')

    data_qrels_llm = None
    if path_to_data_llm_judgments.exists():
        with open(path_to_data_llm_judgments, "rb") as pickle_file :
            data_qrels_llm = pickle.load(pickle_file)

    if data_qrels_llm is not None :
        data_qrels_llm['label'] = data_qrels_llm['relevance_llm']
        data_qrels_llm['quality'] = data_qrels_llm['quality_llm']
        assert len(s.LLMS_TO_USE) == 1
        name = s.LLMS_TO_USE[0]
        if name == s.CLAUDE :
            criteria = 'relevance_claude'
        assert data_qrels_llm[criteria].tolist() == data_qrels_llm['label'].tolist()
    return data_qrels_llm

def get_qrels_human_annotation():
    path_to_data_human_judgments = location_storage / 'data_qrels' / (s.dataset_name_short + '.pkl')
    os.makedirs(path_to_data_human_judgments.parent, exist_ok=True)
    if path_to_data_human_judgments.exists():
        with open(path_to_data_human_judgments , "rb") as pickle_file :
            data_qrels = pickle.load(pickle_file) # includes human knowledge

    else :
        dataset = get_dataset(f'irds:{s.dataset}')
        data_qrels = dataset.get_qrels()
        data_qrels = filter_out_irrelevant_qrels(data_qrels)
        with open(path_to_data_human_judgments, "wb") as pickle_file :
            pickle.dump(data_qrels, pickle_file)
    return data_qrels


def get_qrels(just_human_qrels=False, ignore_qrels_to_use=False):

    # if (s.QRELS_TO_USE_DF is not None) and not ignore_qrels_to_use:
    #     return s.QRELS_TO_USE_DF

    data_qrels_human = get_qrels_human_annotation()
    data_qrels = data_qrels_human

    # if not just_human_qrels and not s.ONLY_HUMAN_QRELS:
    #     logger.info("Getting existing LLM annotations")
    #     data_qrels_llm = get_qrels_llm_annotation()
    #     if data_qrels_llm is not None:
    #         data_qrels = pd.concat([data_qrels , data_qrels_llm] , ignore_index=True)

    qrels = data_qrels[['qid','docno','label']].copy()
    qrels.loc[: , "label"] = qrels["label"].replace({-2 : 0})

    return qrels

def process_touche20(df):
    df['query'] = df['text'].str.lower().str.replace(r'[.?!]' , '' , regex=True)
    return df

# do formatting for single involved string
def process_topic_entry(entry):
    entry_form = re.sub(r'[.?!]', '', entry.lower())  # Remove punctuation using regex
    return entry_form

def get_dataset_queries():
    path_to_data = location_storage / 'data_topics' / (s.dataset_name_short + '.pkl')
    os.makedirs(path_to_data.parent, exist_ok=True)
    if path_to_data.exists() :
        with open(path_to_data , "rb") as pickle_file :
            loaded_data = pickle.load(pickle_file)
            return loaded_data[['qid','query']]

    dataset = get_dataset(f'irds:{s.dataset}')
    queries = dataset.get_topics()

    if s.dataset_name_short == 'touche20': # do additional processing for Touche20
        queries = process_touche20(queries)

    with open(path_to_data , "wb") as pickle_file :
        pickle.dump(queries , pickle_file)
    return queries[['qid','query']]

# get overview hom many QRELS are from human for this dataset, how many are from LLM
def get_qrels_human_llm_stats(df):

    path_to_data = location_storage / 'data_qrels' / (s.dataset_name_short + '.pkl')
    os.makedirs(path_to_data.parent, exist_ok=True)

    all_qrels_df = get_qrels(ignore_qrels_to_use=True)
    all_qrels_human_df = get_qrels(just_human_qrels=True, ignore_qrels_to_use=True)

    if s.QRELS_TO_USE_DF is not None: # we have to adjust the included datasets
        all_qrels_df = s.QRELS_TO_USE_DF

    llm_annotation_df_tmp = all_qrels_df.merge(all_qrels_human_df , on=['qid' , 'docno'] , how='left', indicator=True)
    llm_annotation_df = llm_annotation_df_tmp[llm_annotation_df_tmp['_merge'] == 'left_only'].drop(columns=['_merge'])

    human_annotation_hum_tmp = all_qrels_df.merge(all_qrels_human_df, on=['qid', 'docno'], how='left', indicator=True)
    human_annotation_df = human_annotation_hum_tmp[human_annotation_hum_tmp['_merge'] == 'both'].drop(columns=['_merge'])

    df_current_retriever = df[['qid' , 'docno']]
    all_qrels_df = all_qrels_df[['qid' , 'docno']]
    all_qrels_llm_df = llm_annotation_df[['qid' , 'docno']]

    # Merge the two DataFrames on 'qid' and 'docno'
    merge_retriever_all_df = pd.merge(df_current_retriever , all_qrels_df, on=['qid', 'docno'], how='inner')
    count_merge_retriever_all_df = len(merge_retriever_all_df)

    # get number of llm annotations
    merge_retriever_llm_df = pd.merge(df_current_retriever , all_qrels_llm_df,on=['qid', 'docno'], how='inner')
    count_merge_retriever_llm_df = len(merge_retriever_llm_df)

    assert count_merge_retriever_all_df == len(df)
    assert  len(human_annotation_df) + len(llm_annotation_df) == len(all_qrels_df)
    logger.info(f"All Qrels: {len(all_qrels_df)}")
    logger.info(f"All Qrels Human: {len(human_annotation_df)}")
    logger.info(f"All Qrels LLM: {len(llm_annotation_df)}")

    logger.info(f"Retriever Qrels: {count_merge_retriever_all_df}")
    logger.info(f"Retriever Qrels Human: {len(df)-count_merge_retriever_llm_df}")
    logger.info(f"Retriever Qrels LLM: {count_merge_retriever_llm_df}")


def update_dataset_llm_qrels(data_dict):
    path_to_data_llm = location_storage / 'data_qrels' / (s.dataset_name_short + '_llm_annotation.pkl')
    os.makedirs(path_to_data_llm.parent , exist_ok=True)

    data_dict.update({'iteration' : 0})
    data_dict_keys = list(data_dict.keys())
    if path_to_data_llm.exists() :
        with open(path_to_data_llm , "rb") as pickle_file :
            qrels_df = pickle.load(pickle_file)
    else:

        qrels_df = pd.DataFrame(columns=data_dict_keys)

    # Create a new DataFrame with the new row
    new_row = pd.DataFrame([data_dict])

    # Check if the new row already exists in the existing DataFrame
    exists = not qrels_df.merge(new_row ,on=data_dict_keys, how='inner').empty

    if not exists:
        # Concatenate the new row to the existing DataFrame
        qrels_df = pd.concat([qrels_df , new_row] , ignore_index=True)

    with open(path_to_data_llm , "wb") as pickle_file :
        pickle.dump(qrels_df , pickle_file)


if __name__ == '__main__':

    s.set_data_manually('touche20')
    get_qrels()
    get_dataset_queries()

    dataset = get_dataset(f'irds:{s.dataset}')
    data_qrels = dataset.get_qrels()

    path = '/Users/max/projects/axiomatic-reranking/_additional_data/touche-task1-51-100-relevance.qrels'
    data = df = pd.read_csv(path , sep=' ' , header=None)
    data.columns = ['qid' , 'col2' , 'docno' , 'label']
    df1 = data[['qid' , 'docno' , 'label']].copy()
    df2 = data_qrels[['qid' , 'docno' , 'label']].copy()
    df1.loc[: , 'qid'] = df1['qid'].astype(int)
    df1.loc[: , 'label'] = df1['label'].astype(int)
    df2.loc[: , 'qid'] = df2['qid'].astype(int)
    df2.loc[: , 'label'] = df2['label'].astype(int)

    # Compare the DataFrames
    for index in range(len(df1)) :
        # Get the rows to compare
        row1 = df1.iloc[index]
        row2 = df2.iloc[index]

        # Find columns where values differ
        differing_columns = row1[row1 != row2].index.tolist()

        # Print the index and differing columns
        if differing_columns :
            print(f"Row {index} differs in columns: {differing_columns}")
            for col in differing_columns :
                print(f" - df1[{col}]: {row1[col]} vs df2[{col}]: {row2[col]}")
