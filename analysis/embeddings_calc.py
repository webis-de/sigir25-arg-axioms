import settings as s
from utils.save_runs import load_runs
from collections import defaultdict
import analysis.touche_participants_analysis as tpa
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.manifold import MDS
import copy

a = load_runs('touche21-rerank-top10-human-eval')
print(tpa.metric_list[0][tpa.NAME_KEY])

eval_top_5 = tpa.ToucheRerankingAnalysis(a, tpa.metric_list[0][tpa.NAME_KEY])
eval_top_10 = tpa.ToucheRerankingAnalysis(a, tpa.metric_list[1][tpa.NAME_KEY])


# implement a shortened representation of tex

# Used to map the keys to the correct names for display
arg_translate_dict_tmp = {
    'QSenSim_max_exact_sbert': r'QS_{e}\!\!\uparrow\!\!',
    'QSenSim_max_sbert' : r'QS\!\!\uparrow\!\!',

    'QSenSim_mean_exact_sbert' : r'\overline{QS_{e}}',
    'QSenSim_mean_sbert' : r'\overline{QS}',

    'QArgSim_max_exact_sbert_full_document' : r'QA_{e}\!\!\uparrow\!\!',

    'QArgSim_max_sbert_full_document' : r'QA\!\!\uparrow\!\!',

    'QArgSim_mean_exact_sbert_full_document' : r'\overline{QA_{e}}',

    'QArgSim_mean_sbert_full_document' : r'\overline{QA}\!\!',
}


def create_data(score_metric):
    axioms_vectors_dict = defaultdict(list) # all keys are axioms and value is list of score for the group
    axioms_to_use_list = []

    for participant,metric_dict in score_metric.data_dicts_participants.items():
        axioms_list = metric_dict[tpa.AXIOM_KEY]
        axioms_to_use_list.extend(axioms_list)

    axioms_to_use_list = sorted(list(set(axioms_to_use_list)))
    for participant,metric_dict in score_metric.data_dicts_participants.items():
        for axiom in axioms_to_use_list:
            id = metric_dict[tpa.AXIOM_KEY].index(axiom)
            value = metric_dict[tpa.SCORE_KEY_RAW][id]
            axioms_vectors_dict[axiom].append(value)

    # create corresponding dataframe in differences
    df_score_subtracted = pd.DataFrame(axioms_vectors_dict)
    df_score_subtracted = df_score_subtracted.subtract(df_score_subtracted['base'], axis=0)
    df_score_subtracted = df_score_subtracted.drop(columns=['base'])

    # create corresponding dataframe just for score
    vectors_to_work_with = copy.deepcopy(axioms_vectors_dict)
    del vectors_to_work_with['base']
    df_score = pd.DataFrame(vectors_to_work_with)

    # do calculation of the underlying
    df_sub_copy = df_score_subtracted.copy()
    df_sub_copy[df_sub_copy < 0]= 0

    column_dict = df_sub_copy.sum().to_dict()

    return df_score, df_score_subtracted, column_dict



def calculate_similarity_difference(df,description,ax=None,effect=None):

    array = df.T.values
    cos_sim_matrix = cosine_similarity(array)
    cos_sim_df = pd.DataFrame(cos_sim_matrix, index=df.columns, columns=df.columns)
    print("\nCosine Similarity Between Columns:")
    print(cos_sim_df.to_string())

    distance_matrix = pairwise_distances(cos_sim_df, metric='euclidean')
    print("\nDistance Matrix (Cosine Distance):\n", distance_matrix)

    # Perform clustering on the distance matrix
    clustering = DBSCAN(eps=1.5, min_samples=2, metric='precomputed')
    labels = clustering.fit_predict(distance_matrix)

    # Use MDS to reduce the distance matrix to 2D
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    embeddings = mds.fit_transform(distance_matrix)
    print(embeddings)

    # Get names from the DataFrame index or a specific column
    names_orig = cos_sim_df.index
    # Get Latex Representation of the names
    names = []

    if effect is not None: # in this case we add the corresponding effectsize to the axioms
        for name in names_orig:
            names.append(f"${arg_translate_dict_tmp[name]}$\n${effect[name]:.2f}$")
    else:
        for name in names_orig:
            names.append(f"${arg_translate_dict_tmp[name]}$")


    # we just want to show the corresponding points
    unique_labels = np.unique(labels)

    if ax is None:
        # Create figure
        fig, ax = plt.subplots(figsize=(6, 6))

    # Plot clusters
    ax.scatter(embeddings[:, 0], embeddings[:, 1], color='black',s=100)  # No labels

    # Annotate points with names
    for i, (x, y) in enumerate(embeddings) :
        ax.annotate(names[i], (x, y), textcoords="offset points", xytext=(-10,-25),
                    ha='right', fontsize=14, color='black')

    ax.legend()
    ax.tick_params(direction='in')

    ax.margins(x=0.2, y=0.03)

    # ax.margins(x=0.2, y=0.15) # nDCG 10
    # ax.set_title(f"Axiom Difference Similarity - {description}")
    # Set axis limits
    #ax.set_xlim(-0.1, 0.2)
    #ax.set_ylim(-0.2, 0.14)

    # Axiom Absolute Similiarity



if __name__ == '__main__':
    ev5_score, ev5_substracted, effect5 = create_data(eval_top_5)
    ev10_score, ev10_substracted, effec10 = create_data(eval_top_10)

    # fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(10, 12))
    #calculate_similarity_difference(ev5_substracted,"NDCG5",None,effect=effect5)
    calculate_similarity_difference(ev10_substracted,"NDCG10",None,effect=effec10)

    plt.tight_layout()
    # Save the figure containing both plots.
    filename = "ndcg5.pdf"
    plt.savefig(filename, dpi=300, bbox_inches='tight',format='pdf')

    plt.show()

    #calculate_similarity_difference(ev5_score,"NDCG5")
    #calculate_similarity_difference(ev10_score,"NDCG10")
