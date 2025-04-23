from ir_axioms.axiom import Axiom
from ir_axioms.axiom.utils import strictly_greater , approximately_equal
from axioms.utils.socket_communication import document_ranking_socket_sent,transmission_dict
import settings as s
class STMC1_sbert(Axiom):
    name = "STMC1_sbert"

    def preference(self, context, query, document1, document2) -> float:
        q_terms = context.term_set(query)
        doc1_terms = context.term_set(document1)
        doc2_terms = context.term_set(document2)
        query_text = query.title

        document1_data = transmission_dict(id=document1.id, document=doc1_terms, embedding_model=s.SBERT, embedding_style=s.SMTC1, sentenize=False)
        document2_data = transmission_dict(id=document2.id, document=doc2_terms, embedding_model=s.SBERT, embedding_style=s.SMTC1, sentenize=False)
        query_vector = transmission_dict(id=query_text, document=q_terms, embedding_model=s.SBERT,
                                         embedding_style=s.SMTC1, sentenize=False)

        ranking_data = document_ranking_socket_sent(document1_data, document2_data, query_vector, s.MEAN, task=s.SMTC1)

        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]

        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )
