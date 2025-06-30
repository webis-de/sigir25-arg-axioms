import pyterrier as pt
from pathlib import Path
import ir_measures

# Initialize PyTerrier JVM if not started yet
if not pt.java.started():
    pt.java.init()

from pyterrier.pipelines import Experiment
from pyterrier.datasets import get_dataset

# Import axiomatic reranking modules
from ir_axioms.modules.pivot import MiddlePivotSelection
from ir_axioms.backend.pyterrier.transformers import KwikSortReranker
from ir_axioms.axiom import AND

# Import cache path from settings or define your own cache directory
from settings import CACHE_PATH


def kwiksort(reranker_base, axioms, rerank_num, index_path, cache_dir):
    """
    Perform axiomatic KwikSort reranking on top of a base retrieval system.

    Args:
        reranker_base: Base retrieval system (e.g., Terrier DirichletLM).
        axioms: List of axioms (e.g., [AND()]) to apply.
        rerank_num: Number of top documents to rerank.
        index_path: Path to the Terrier index.
        cache_dir: Directory to store cache for reranking.

    Returns:
        List of reranked retrieval pipelines (one per axiom).
    """
    results = []
    for axiom in axioms:
        kwik_reranker = KwikSortReranker(
            axiom=axiom,
            index=index_path,
            pivot_selection=MiddlePivotSelection(),
            cache_dir=cache_dir
        )
        # Compose the pipeline:
        # Retrieve top rerank_num documents, rerank them with kwiksort, then merge scores with base retriever
        reranked_pipeline = reranker_base % rerank_num >> kwik_reranker ^ reranker_base
        results.append(reranked_pipeline)
    return results


if __name__ == '__main__':

    # Define index and cache directories relative to this script, Code how to build the index is in the index directory
    INDEX_PATH = Path(__file__).parent / "_touche21_index"
    CACHE_PATH = Path(__file__).parent / "_cache_dir"

    # Load Terrier index reference and factory for statistics or advanced operations
    indexref = pt.IndexRef.of(str(INDEX_PATH))
    index = pt.IndexFactory.of(indexref)
    stat = index.getCollectionStatistics()

    # Number of documents to rerank
    rerank_nbr = 5

    # Load dataset: TOUCHE 2021 task 1, replace if you want another dataset
    dataset = get_dataset("irds:argsme/2020-04-01/touche-2021-task-1")

    # Fetch queries and qrels for evaluation
    queries = dataset.get_topics()
    qrels = dataset.get_qrels()
    print(f'Number of queries: {len(queries)}')

    # Baseline retrieval: Dirichlet Language Model
    dirichletLM = pt.terrier.Retriever(indexref, wmodel="DirichletLM")

    # Retrieve initial results for all queries
    baseline_results = dirichletLM.transform(queries)
    print("Baseline retrieval sample results:")
    print(baseline_results.head())

    # Define evaluation metrics for IR experiment
    metrics = [
        ir_measures.nDCG(judged_only=True) @ 5,
        ir_measures.nDCG() @ 5,
    ]
    # Metric names aligned with experiment results
    metrics_names = ['nDCG(judged_only=True)@5', 'nDCG(judged_only=True)@10', 'nDCG@5', 'nDCG@10']

    # Define axioms for reranking, here only AND axiom as example
    axioms_list = [AND()]
    axioms_names_list = ["AND"]

    # Perform KwikSort reranking for all axioms
    rerank_pipelines = kwiksort(dirichletLM, axioms_list, rerank_nbr, INDEX_PATH, CACHE_PATH)

    # Preview reranked results for the first axiom on all queries
    reranked_results_df = rerank_pipelines[0].transform(queries)
    print("Sample reranked results (first axiom):")
    print(reranked_results_df.head())

    # Run an IR experiment comparing baseline and reranked systems
    experiment = Experiment(
        retr_systems=[dirichletLM] + rerank_pipelines,
        topics=queries,
        qrels=qrels,
        eval_metrics=metrics,
        names=["dirichlet"] + axioms_names_list,
        baseline=0,
        correction="bonferroni",
        verbose=True,
    )

    # Sort experiment results by the first metric descending
    experiment.sort_values(by=metrics_names[0], ascending=False, inplace=True)
    print("\nExperiment results summary:")
    print(experiment)
