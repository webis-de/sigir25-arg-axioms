import sys

import settings as s
import pyterrier as pt
import ir_measures
from pyterrier.pipelines import Experiment
import utils.repair_result_dataframe as rd
from utils.base_transformer import ResultTransformer
import utils.get_datafeatures_from_datasets as gdf
from loguru import logger
from pyterrier.datasets import get_dataset

# evaluation of a single run of a Touche participant, used to return the corresponding NDCG, to determine best run.
# based on these results, the best run is selected and used for the reranking task with axioms.

def evaluate_single_touche_run_ndcg(ndcg_nbr,group_name,df):
    if not pt.java.started() :
        pt.java.init()

    filtered_df = rd.cut_retrieval_results_top_n(df,ndcg_nbr)
    if filtered_df is None:
        logger.error(f"Run {group_name} has not enough judgments for NDCG@{ndcg_nbr}, skipping")
        return None

    # gdf.get_qrels_human_llm_stats(filtered_df)

    filtered_df_transform = ResultTransformer(filtered_df)

    ndcg_judge_only_name = 'nDCG(judged_only=True)@{}'.format(ndcg_nbr)
    ndcg_judge_only = ir_measures.nDCG(judged_only=True)@ndcg_nbr

    ndcg_judge_alternative = ir_measures.nDCG(dcg='exp-log2')@ndcg_nbr
    dcg_judge_alternative_name = 'nDCG(dcg=\'exp-log2\')@5'
    ndcg_name = 'nDCG@{}'.format(ndcg_nbr)
    ndcg = ir_measures.nDCG()@ndcg_nbr

    #dataset = get_dataset(f'irds:{s.dataset}')
    #qrels = dataset.get_qrels()
    #qrels.loc[:, "label"] = qrels["label"].replace({-2 : 0})
    #qrels = qrels[["qid","docno","label"]]

    # two variants which should result exact the same output
    experiment = Experiment(
        retr_systems= [filtered_df_transform,pt.Transformer.from_df(filtered_df)],
        topics= gdf.get_dataset_queries(),
        qrels= gdf.get_qrels(),
        eval_metrics=[ndcg,ndcg_judge_only,ndcg_judge_alternative],
        names=[group_name,'reference'],
        verbose=True,
    )

    # ensure not unjudged documents were used
    all_vals_judge = experiment[ndcg_judge_only_name].values.tolist()
    all_vals = experiment[ndcg_name].values.tolist()

    def round_float(data_list):
        return [round(float(x), 5) if isinstance(x, float) else x for x in data_list]

    all_vals_judge = round_float(all_vals_judge)
    all_vals = round_float(all_vals)

    merged_set = set(all_vals + all_vals_judge)
    if len(merged_set) != 1:
        logger.error(f"Error in evaluation of {group_name} , values are not the same: {merged_set}")
        sys.exit()
    score_to_use = experiment.loc[experiment['name'] == group_name, ndcg_name].values[0]
    return score_to_use