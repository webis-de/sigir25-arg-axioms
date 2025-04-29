
# basic specification how the reranking shall be done for the new axioms
# Therefore this function can be used in various reranking experiments
from typing import Iterable

import pandas as pd
import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import matplotlib.pyplot as plt

import utils.repair_result_dataframe as rd
import ir_measures
import settings as s
from pyterrier.pipelines import Experiment
from axioms.qsensim_sbert import QSenSim_max_exact_sbert,QSenSim_max_sbert, QSenSim_mean_exact_sbert,QSenSim_mean_sbert
from axioms.qargsim_sbert import QArgSim_max_exact_sbert,QArgSim_max_sbert, QArgSim_mean_exact_sbert,QArgSim_mean_sbert
from axioms.stmc_sbert import STMC1_sbert
import utils.get_datafeatures_from_datasets as gdf
from experiments.kwiksort import kwiksort

#s.set_dataset('touche20')
ndcg_nbr = 5

class base_transformers(pt.Transformer):
    def __init__(self,dataframe):
        super().__init__()
        self.dataframe = dataframe
        self.transform_own =  pt.Transformer.from_df(dataframe, uniform=True)
    def transform(self, input):

        result = self.transform_own.transform(input)
        return result

    def __mod__(self , right: int) :
        filtered_df = self.dataframe[(self.dataframe['rank'] >= 0) & (self.dataframe['rank'] <= (right - 1))]
        return filtered_df

    def __xor__(self, right : 'Transformer') -> 'Transformer':
        return self.transform_own ^ right


if __name__ == '__main__':
    dirichletLM = pt.terrier.Retriever(str(s.DATASET_INDEX_DIR), wmodel="DirichletLM")
    bm25 = pt.terrier.Retriever(str(s.DATASET_INDEX_DIR), wmodel="BM25")

    dirichletLM_result = dirichletLM.transform(gdf.get_dataset_queries())

    rd.adjust_retrieval_results_dataframe(dirichletLM_result,ndcg_nbr)
    filtered_df = rd.repair_rank_retrieval_results_dataframe_drop_missing(dirichletLM_result)
    filtered_df_transform = base_transformers(filtered_df)



    new_axioms = [  STMC1_sbert(),
                    QSenSim_max_exact_sbert(),
                    QSenSim_max_sbert() ,

                    QSenSim_mean_exact_sbert() ,
                    QSenSim_mean_sbert(),

                    QArgSim_max_exact_sbert() ,
                    QArgSim_max_sbert() ,

                    QArgSim_mean_exact_sbert(),
                    QArgSim_mean_sbert()
                  ]



    new_axioms_names = [
        'STMC1_sbert',

        'QSenSim_max_exact_sbert' ,
        'QSenSim_max_sbert' ,

        'QSenSim_mean_exact_sbert' ,
        'QSenSim_mean_sbert' ,

        'QArgSim_max_exact_sbert' ,
        'QArgSim_max_sbert' ,

        'QArgSim_mean_exact_sbert' ,
        'QArgSim_mean_sbert'
                  ]

    rerank_initial = kwiksort(filtered_df_transform, new_axioms,ndcg_nbr)

    experiment = Experiment(
        retr_systems=[filtered_df,bm25,dirichletLM] + rerank_initial,
        topics=gdf.get_dataset_queries(),
        qrels=gdf.get_qrels(),
        filter_by_topics=True,
        eval_metrics=[ir_measures.nDCG(judged_only=True) @ ndcg_nbr,ir_measures.nDCG() @ ndcg_nbr],
        names=['dirichlet_only_qrels','bm25','dirichlet'] + new_axioms_names,
        baseline=0,
        correction="bonferroni",
        verbose=True,
    )
    experiment.sort_values(by=f"nDCG(judged_only=True)@{ndcg_nbr}", ascending=False, inplace=True)
    df = experiment[["name",f"nDCG(judged_only=True)@{ndcg_nbr}",f"nDCG@{ndcg_nbr}"]]


    df[f"nDCG(judged_only=True)@{ndcg_nbr}"] = df[f"nDCG(judged_only=True)@{ndcg_nbr}"].round(3)
    df[f"nDCG@{ndcg_nbr}"] = df[f"nDCG@{ndcg_nbr}"].round(3)


    # Create a figure and axis
    fig , ax = plt.subplots(figsize=(11.69 , 8.27))  # A4 landscape size in inches

    # Hide axes
    ax.axis('off')

    # Create a table and add it to the axes
    table = ax.table(cellText=df.values , colLabels=df.columns , cellLoc='center' , loc='center')

    # Adjust column width based on text
    for i , col in enumerate(df.columns) :
        max_length = max(df[col].astype(str).map(len).max() , len(col))  # Get max length of column
        table.auto_set_column_width(i)  # Automatically adjust width based on content
        table.scale(max_length / 5 , 1)  # Scale the width

    # Increase row height by scaling the height
    row_height = 2  # Adjust this value to increase/decrease height
    table.scale(1 , row_height)  # Scale width by 1 (unchanged) and height by row_height

    # Set the table font size
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Adjust layout
    plt.subplots_adjust(left=0.2 , right=0.8 , top=0.8 , bottom=0.2)

    # Save as PDF (landscape)
    plt.savefig('dataframe_landscape.pdf' , format='pdf' , bbox_inches='tight')
    plt.show()

    # Create a figure and axis
    mewo = 3