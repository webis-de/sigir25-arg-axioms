from ir_axioms.axiom import Axiom
from ir_axioms.axiom.utils import approximately_equal, strictly_greater

import settings as s
from axioms.utils.socket_communication import _preference_vectors

# these axioms are designed to utilize TARGER's own sentencizer, therefore the whole document is given to TARGER
class QArgSim_mean_exact_sbert_full_document(Axiom):
    name = "QArgSim_mean_exact_sbert_targer_full_document"
    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method=s.MEAN,
                                           document_sentenice= False,
                                           embedding_style= s.STYLE_AUS_FULL_DOCUMENT,
                                           task=s.DOCUMENT_RANKING,
                                           task_info= {s.TASK_INFO_TARGER_OWN_SENTENICER : True}
                                           )

        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )


class QArgSim_mean_sbert_full_document(Axiom):
    name = "QArgSim_mean_approxequal_sbert_full_document"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method=s.MEAN,
                                           document_sentenice=False,
                                           embedding_style=s.STYLE_AUS_FULL_DOCUMENT,
                                           task=s.DOCUMENT_RANKING,
                                           task_info={s.TASK_INFO_TARGER_OWN_SENTENICER : True}

                                           )
        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        if approximately_equal(doc1_similarity,doc2_similarity):
            return 0
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )



class QArgSim_max_exact_sbert_full_document(Axiom):
    name = "QArgSim_max_exact_sbert_full_document"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method= s.MAX,
                                           document_sentenice=False,
                                           embedding_style=s.STYLE_AUS_FULL_DOCUMENT,
                                           task=s.DOCUMENT_RANKING,
                                           task_info={s.TASK_INFO_TARGER_OWN_SENTENICER : True}

                                           )
        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )


class QArgSim_max_sbert_full_document(Axiom):
    name = "QArgSim_max_approxequal_sbert_full_document"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method= s.MAX,
                                           document_sentenice=False,
                                           embedding_style=s.STYLE_AUS_FULL_DOCUMENT,
                                           task = s.DOCUMENT_RANKING,
                                           task_info={s.TASK_INFO_TARGER_OWN_SENTENICER : True}
                                           )

        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        if approximately_equal(doc1_similarity,doc2_similarity):
            return 0
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )
