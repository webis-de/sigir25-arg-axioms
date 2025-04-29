import numpy as np
from numpy import var
from math import sqrt
from utils.save_runs import load_runs
from axioms.axioms_names import arg_axiom_list_new_axioms,arg_axiom_name_list_new_axioms,axiom_list_old_axioms,axiom_names_list_old_axioms
from scipy import stats
experiment = load_runs('dirichletlm-reranking-touche21-top10-effectsize')

baseline = 'baseline-dirichlet'


dirichlet_metrics_ndcg5 = experiment[(experiment['name'] == baseline) & (experiment['measure'] == 'nDCG@5')][
    'value'].values

assert len(dirichlet_metrics_ndcg5) == len(experiment['qid'].unique())

dirichlet_metrics_ndcg10 = experiment[(experiment['name'] == baseline) & (experiment['measure'] == 'nDCG@10')][
    'value'].values



# function to calculate Cohen's d for independent samples
def cohend(d1,d2):
	# calculate the size of samples
	n1, n2 = len(d1), len(d2)
	# calculate the variance of the samples
	s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
	# calculate the pooled standard deviation
	s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
	# calculate the means of the samples
	u1, u2 = np.mean(d1), np.mean(d2)
	# calculate the effect size
	return (u1 - u2) / s


significant_ndcg5 = []
significant_ndcg10 = []

for name in arg_axiom_name_list_new_axioms :

    axiom_ndcg5 = experiment[(experiment['name'] == name) & (experiment['measure'] == 'nDCG@5')][
        'value'].values
    axiom_ndcg10 = experiment[(experiment['name'] == name) & (experiment['measure'] == 'nDCG@10')][
        'value'].values

    print('Axiom:',name)
    print("Mean nDCG@5:",np.mean(axiom_ndcg5))
    print("Mean nDCG@10:",np.mean(axiom_ndcg10))

    t_test5 = stats.ttest_rel(dirichlet_metrics_ndcg5, axiom_ndcg5)
    effect_size5 = cohend(dirichlet_metrics_ndcg5,axiom_ndcg5)
    effect_size10 = cohend(dirichlet_metrics_ndcg10,axiom_ndcg10)
    b = stats.ttest_rel(axiom_ndcg5, dirichlet_metrics_ndcg5)
    print( 'T-test nDCG@5:',t_test5.pvalue)
    print( 'T-test :',b.pvalue)
    if t_test5.pvalue < 0.05/50:
        print('Significant nDCG@5')
        significant_ndcg5.append(effect_size5)
    t_test10 = stats.ttest_rel(dirichlet_metrics_ndcg10, axiom_ndcg10)
    if t_test10.pvalue < 0.05/50:
        print('Significant nDCG@10')
        significant_ndcg10.append(effect_size10)

    print('Cohen nDCG@5:',effect_size5)
    print('Cohen nDCG@5rev:',cohend(axiom_ndcg5,dirichlet_metrics_ndcg5))

    print('Cohen nDCG@10:',effect_size10)
    print('Cohen nDCG@10rev:',cohend(axiom_ndcg10,dirichlet_metrics_ndcg10))
    print('')


print('Significant nDCG@5 Effectsize:',significant_ndcg5)
print('Significant nDCG@10 Effectsize:',significant_ndcg10)