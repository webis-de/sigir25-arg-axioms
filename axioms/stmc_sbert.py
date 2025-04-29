from ir_axioms.axiom import Axiom
from ir_axioms.axiom.utils import approximately_equal, strictly_greater

import settings as s
from axioms.utils.socket_communication import document_ranking_socket_sent, transmission_dict

class STMC1_sbert(Axiom):
    name = "STMC1_sbert"

    def preference(self, context, query, document1, document2) -> float:
        doc1_terms = list(context.term_set(document1))
        doc2_terms = list(context.term_set(document2))
        query_id = query.title
        query_terms = list(context.term_set(query))

        document1_data = transmission_dict(id=document1.id,
                                           document=doc1_terms,
                                           embedding_model=s.SBERT,
                                           embedding_style=s.STMC1,
                                           sentenice=False,
                                           task=s.STMC1)

        document2_data = transmission_dict(id=document2.id,
                                           document=doc2_terms,
                                           embedding_model=s.SBERT,
                                           embedding_style=s.STMC1,
                                           sentenice=False,
                                           task=s.STMC1)

        query_vector = transmission_dict(id=query_id,
                                         document=query_terms,
                                         embedding_model=s.SBERT,
                                         embedding_style=s.STMC1,
                                         sentenice=False,
                                         task=s.STMC1)

        ranking_data = document_ranking_socket_sent(document1_data=document1_data,
                                                    document2_data=document2_data,
                                                    query_data=query_vector,
                                                    comparison=s.MEAN,
                                                    task=s.STMC1)

        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]

        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )
