import settings
from utils.save_runs import save_runs,load_runs
import utils.repair_result_dataframe as rd
from axioms.axioms_names import arg_axiom_list_new_axioms,arg_axiom_name_list_new_axioms, STMC1_sbert, QArgSim_max_sbert_full_document, axiom_list_old_axioms,axiom_names_list_old_axioms
from experiments.utils.reranking_skeleton import re_rank_argu_axioms
from ir_axioms.backend.pyterrier.transformers import KwikSortReranker,RandomPivotSelection

import ir_measures

if __name__ == '__main__':
    #RandomPivotSelection.seed = 42

    settings.set_data_manually('touche21')
    # do reranking for touche21 participants, with the new involved axioms
    experiment_name = 'touche21-rerank-top10-human-eval'

    base_run_data_list = load_runs('touche-21-base_evaluation-human-eval')
    rerank_nbr = 10 # number of documents to rerank

    cmp_nbr = None
    baseline = 'baseline-dirichlet'
    for name,DATA in base_run_data_list :
        if DATA[0] == baseline:
            cmp_nbr = DATA[2]

    best_runs = []
    for i, (name, DATA) in enumerate(base_run_data_list):
        print(i,len(base_run_data_list))
        if DATA[2] >= cmp_nbr: # only use the runs which are better than the baseline
            group = DATA[0]
            best_run = DATA[3]
            rd.repair_rank_retrieval_results_dataframe_drop_missing(best_run)
            best_runs.append((group,best_run))


    metrics = [ir_measures.nDCG(judged_only=True) @ 5, ir_measures.nDCG(judged_only=True) @ 10, ir_measures.nDCG() @ 5,
               ir_measures.nDCG() @ 10]
    metric_names = ['nDCG(judged_only=True)@5', 'nDCG(judged_only=True)@10', 'nDCG@5', 'nDCG@10']

    axioms = arg_axiom_list_new_axioms # [QArgSim_max_sbert_full_document()]
    axioms_names = arg_axiom_name_list_new_axioms # ["QArgSim"]

    re_ranked_data_participants = []
    for group, df in best_runs: # loop through all groups and save data as dict
        experiment_group = re_rank_argu_axioms(group,
                                         df,
                                         axioms=axioms,
                                         axioms_names=axioms_names,
                                         metrics=metrics,
                                         metrics_names=metric_names,
                                         rerank_nbr=rerank_nbr)
        re_ranked_data_participants.append((group,experiment_group))

    save_runs(re_ranked_data_participants, experiment_name)