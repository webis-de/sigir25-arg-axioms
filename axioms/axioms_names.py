from ir_axioms.axiom import (
    AND,
    ANTI_REG,
    ASPECT_REG,
    DIV,
    LB1,
    LEN_AND,
    LEN_DIV,
    LEN_M_AND,
    LEN_M_TDC,
    LNC1,
    M_AND,
    M_TDC,
    PROX1,
    PROX2,
    PROX3,
    PROX4,
    PROX5,
    REG,
    RS_BM25,
    RS_PL2,
    RS_QL,
    RS_TF,
    RS_TF_IDF,
    STMC1,
    STMC2,
    TF_LNC,
    TFC1,
    TFC3,
    ANTI_REG_f,
    ArgUC,
    ASPECT_REG_f,
    QTArg,
    QTPArg,
    REG_f,
    STMC1_f,
    STMC2_f,
    aSL,
)

from axioms.qargsim_sbert import (
    QArgSim_max_exact_sbert_full_document,
    QArgSim_max_sbert_full_document,
    QArgSim_mean_exact_sbert_full_document,
    QArgSim_mean_sbert_full_document,
)
from axioms.qsensim_sbert import (
    QSenSim_max_exact_sbert,
    QSenSim_max_sbert,
    QSenSim_mean_exact_sbert,
    QSenSim_mean_sbert,
)
from axioms.stmc_sbert import STMC1_sbert

arg_axiom_list_new_axioms = [
    QSenSim_max_exact_sbert(),
    QSenSim_max_sbert(),

    QSenSim_mean_exact_sbert(),
    QSenSim_mean_sbert(),

    #QArgSim_max_exact_sbert(),
    QArgSim_max_exact_sbert_full_document(),

    #QArgSim_max_sbert(),
    QArgSim_max_sbert_full_document(),

    #QArgSim_mean_exact_sbert(),
    QArgSim_mean_exact_sbert_full_document(),

    #QArgSim_mean_sbert(),
    QArgSim_mean_sbert_full_document(),
]


arg_axiom_name_list_new_axioms = [
    'QSenSim_max_exact_sbert',
    'QSenSim_max_sbert',

    'QSenSim_mean_exact_sbert',
    'QSenSim_mean_sbert',

    #'QArgSim_max_exact_sbert',
    'QArgSim_max_exact_sbert_full_document',

    #'QArgSim_max_sbert',
    'QArgSim_max_sbert_full_document',

    #'QArgSim_mean_exact_sbert',
    'QArgSim_mean_exact_sbert_full_document',

    #'QArgSim_mean_sbert',
    'QArgSim_mean_sbert_full_document',

]

axiom_list_old_axioms = [ArgUC(), QTArg(), QTPArg(), aSL(),
                         LNC1(), TF_LNC(), LB1(),
                         PROX1(), PROX2(), PROX3(), PROX4(), PROX5(),
                         REG(), REG_f(), ANTI_REG(), ANTI_REG_f(), ASPECT_REG(), ASPECT_REG_f(),
                         AND(), LEN_AND(), M_AND(), LEN_M_AND(), DIV(), LEN_DIV(),
                         RS_TF(), RS_TF_IDF(), RS_BM25(), RS_PL2(), RS_QL(),
                         TFC1(), TFC3(), M_TDC(), LEN_M_TDC(),
                         STMC1_sbert(),
                         STMC1(), STMC1_f(), STMC2(), STMC2_f(),
                         ]



axiom_names_list_old_axioms = ["ArgUC", "QTArg", "QTPArg", "aSL",
            "LNC1", "TF_LNC", "LB1",
            "PROX1", "PROX2", "PROX3", "PROX4", "PROX5",
            "REG_w", "REG_f", "ANTI_REG_w", "ANTI_REG_f", "ASPECT_REG_w", "ASPECT_REG_f",
            "AND", "LEN_AND", "M_AND", "LEN_M_AND", "DIV", "LEN_DIV",
            "RS_TF", "RS_TF_IDF", "RS_BM25", "RS_PL2", "RS_QL",
            "TFC1", "TFC3", "M_TDC", "LEN_M_TDC",
            'STMC1_sbert',
            "STMC1_w", "STMC1_f", "STMC2_w", "STMC2_f",
                               ]

'''
new_axioms_test_ada = [

    QSenSim_max_exact_ada(),
    QSenSim_max_ada(),

    QSenSim_mean_exact_ada(),
    QSenSim_mean_ada(),

    QArgSim_max_exact_ada(),
    QArgSim_max_ada(),

    QArgSim_mean_exact_ada(),
    QArgSim_mean_ada(),
]

new_axioms_names_test_ada = [
    'QSenSim_max_exact_ada',
    'QSenSim_max_ada',

    'QSenSim_mean_exact_ada',
    'QSenSim_mean_ada',

    'QArgSim_max_exact_ada',
    'QArgSim_max_ada',

    'QArgSim_mean_exact_ada',
    'QArgSim_mean_ada',
]
'''

if __name__ == "__main__":
    print(len(arg_axiom_list_new_axioms))
    print(len(arg_axiom_name_list_new_axioms))
    print(len(axiom_list_old_axioms))
    print(len(axiom_names_list_old_axioms))