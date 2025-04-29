import settings as s
import pyterrier as pt
import ir_measures
from pyterrier.pipelines import Experiment
import utils.repair_result_dataframe as rd
from utils.base_transformer import ResultTransformer
import utils.get_datafeatures_from_datasets as gdf
from loguru import logger
from experiments.utils.kwiksort import kwiksort, kwiksort_orig

# re-rank a  base result based on the new axioms, which are investigated
# basic specification how the reranking shall be done for the new axioms
# Therefore this function can be used in various reranking experiments

def re_rank_argu_axioms(group_name,df,axioms=None,axioms_names=None,metrics=None,metrics_names=None,rerank_nbr=None):
    if not pt.java.started():
        pt.java.init()

    filtered_df = rd.cut_retrieval_results_top_n(df, rerank_nbr)
    if filtered_df is None:
        return None

    filtered_df_transform = ResultTransformer(filtered_df)
    rerank_initial = kwiksort(filtered_df_transform, axioms,rerank_nbr)
    rerank_initial_orig = kwiksort_orig(filtered_df_transform, axioms,rerank_nbr)

    experiment = Experiment(
        retr_systems=[filtered_df_transform] + rerank_initial,
        topics=gdf.get_dataset_queries(),
        qrels=gdf.get_qrels(),
        eval_metrics=metrics,
        names=[group_name] + axioms_names,
        baseline=0 ,
        correction="bonferroni",
        verbose=True,
    )

    experiment.sort_values(by=metrics_names[0], ascending=False, inplace=True)
    return experiment