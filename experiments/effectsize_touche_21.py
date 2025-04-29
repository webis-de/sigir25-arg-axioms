import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import matplotlib.pyplot as plt

import utils.repair_result_dataframe as rd
import ir_measures
import settings as s
import utils.get_datafeatures_from_datasets as gdf
from axioms.axioms_names import arg_axiom_list_new_axioms,arg_axiom_name_list_new_axioms,axiom_list_old_axioms,axiom_names_list_old_axioms
from experiments.utils.reranking_effectsize_skeleton import re_rank_argu_axioms_effectsize
import utils.save_runs as sr

if __name__ == '__main__':
    s.set_data_manually('touche21')

    experiment_name = 'dirichletlm-reranking-touche21-top10-effectsize_human_judged'

    indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
    index = pt.IndexFactory.of(indexref)
    stat = index.getCollectionStatistics()

    rerank_nbr = 10  # number of documents to rerank

    queries = gdf.get_dataset_queries()

    dirichletLM = pt.terrier.Retriever(str(s.DATASET_INDEX_DIR), wmodel="DirichletLM")
    res_df = dirichletLM.transform(queries)

    res_df = rd.repair_rank_retrieval_results_dataframe_drop_missing(res_df) # cut df to human judgments only
    res_df = rd.cut_retrieval_results_top_n(res_df, rerank_nbr)


    metrics = [ir_measures.nDCG(judged_only=True)@5,ir_measures.nDCG(judged_only=True)@10,ir_measures.nDCG()@5,ir_measures.nDCG()@10]
    metric_names = ['nDCG(judged_only=True)@5','nDCG(judged_only=True)@10','nDCG@5','nDCG@10']

    axioms = arg_axiom_list_new_axioms
    axioms_names = arg_axiom_name_list_new_axioms

    baseline = 'baseline-dirichlet'

    experiment = re_rank_argu_axioms_effectsize(baseline,
                                                res_df,
                                                axioms=axioms,
                                                axioms_names=axioms_names,
                                                metrics=metrics,
                                                metrics_names=metric_names,
                                                rerank_nbr=rerank_nbr)

    sr.save_runs(experiment, experiment_name)

