from utils import group_name_helpers as gnh
import settings as s
from experiments.touche_participants_reranking.evaluate_single_touche_run_base import evaluate_single_touche_run_ndcg
import utils.repair_result_dataframe as rd
from utils.save_runs import save_runs
from functools import partial

# calculate base performance for the involved touche runs, use it to determine the best run


if __name__ == "__main__":

    # specify the use of touche21
    s.set_data_manually('touche21')

    s.TOUCHE_PARTICIPANT_DIR = '/Users/max/projects/axiomatic-reranking/_touche21_participant_data'
    experiment_name = 'touche-21-base_evaluation_human_eval'
    ndcg_nbr = 5 # first all participants are evaluated on the ndcg@5 metric

    # first get all runs from the participants, every bit of data is pooled
    # this is necessary for getting a united pool of qrels
    score_func_touche21 = partial(evaluate_single_touche_run_ndcg , ndcg_nbr)
    participants = gnh.get_all_group_participants()

    # find the best submitted run for each participant
    data_collection = []
    for name in participants:
        DATA = gnh.get_best_run_for_participant(name, get_run_func=gnh.get_runs_from_participants_touche21, experiment_func=score_func_touche21)
        if DATA[0] is None:
            continue
        data_collection.append((name, DATA))

    save_runs(data_collection, experiment_name)
