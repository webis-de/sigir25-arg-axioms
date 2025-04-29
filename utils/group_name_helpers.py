from pathlib import Path
from pyterrier.io import read_results
import pyterrier
import pickle
from loguru import logger
import re
import settings as s
from slugify import slugify
import utils.repair_result_dataframe as rd
import sys

def get_runs_from_participants_touche21(desired_group_name):
    desired_group_name_slug = slugify(desired_group_name).lower()
    run_files = []

    # cycle through the incorporated files and perform the operations
    for group in Path(s.TOUCHE_PARTICIPANT_DIR).iterdir():
        group_name = slugify(group.name).lower()

        if group_name == desired_group_name_slug:
            group_dir_with_runs = group.joinpath('output-deduplicated-with-copycat')
            if not group_dir_with_runs.exists():
                logger.info(f"Group {desired_group_name} has no deduplicated runs, trying to find runs in output directory")
                #sys.exit(1)
                group_dir_with_runs = group.joinpath('output')
            for run_file in group_dir_with_runs.iterdir():
                run_file_name = slugify(run_file.name).lower()
                run_file_read = read_results(str(run_file)) # read run file with pyterrier
                res_df = rd.repair_touche_run(run_file_read)
                repaired_run_file = rd.repair_rank_retrieval_results_dataframe_drop_missing(res_df)  # cut df to human judgments only

                test_ndcg10 = rd.cut_retrieval_results_top_n(repaired_run_file, 10)
                if test_ndcg10 is None:
                    logger.warning(f"Run {run_file} has not enough judgments for NDCG@10, skipping")
                    continue


                if repaired_run_file is not None:
                    run_files.append((run_file_name, repaired_run_file))
            return run_files
    return None

def get_all_group_participants():
    directories = [slugify(d.name).lower() for d in Path(s.TOUCHE_PARTICIPANT_DIR).iterdir() if d.is_dir()  and not d.name.startswith('.')]
    return directories

def get_best_run_for_participant(group_name,get_run_func=None,experiment_func=None):
    '''Experiment function determines which evaluation is used to determine the best run'''
    group_name_slug = slugify(group_name).lower()
    experiments_results = []
    runs = get_run_func(group_name)
    if len(runs) == 0:
        logger.error(f"No runs found for group {group_name}")
        return None,None,None,None
    best_run_nbr = None
    best_run = None
    best_run_result = - 1
    all_results = []
    for name,run in runs:
        result = experiment_func(group_name,run)
        if result is None: # in case the run cannot be judged
            continue
        all_results.append(result)
        experiments_results.append((name,result))
        if result > best_run_result:
            best_run = run
            best_run_result = result
            best_run_nbr = name
    if best_run is None:
        logger.error(f"No best run found for group {group_name}")
        return None,None,None,None
    avg = sum(all_results) / len(all_results)
    print(f"Average score for {group_name} is {avg}")
    print(f"Best score for {group_name} is {best_run_result}")
    #with open(results_path, 'wb') as f:
     #   pickle.dump((best_run_nbr,best_run,runs,experiments_results),f)
    return group_name_slug, best_run_nbr, best_run_result,best_run,experiments_results






