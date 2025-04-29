class QArgSim_max_sbert(Axiom):
    name = "QArgSim_max_approxequal_sbert"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method= s.MAX,
                                           embedding_style=s.STYLE_AUS_SINGLE_SENTENCE
                                           )

        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        if approximately_equal(doc1_similarity,doc2_similarity):
            return 0
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )


class QArgSim_max_exact_sbert(Axiom):
    name = "QArgSim_max_exact_sbert"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method= s.MAX,
                                           embedding_style=s.STYLE_AUS_SINGLE_SENTENCE

                                           )
        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )


class QArgSim_mean_sbert(Axiom):
    name = "QArgSim_mean_approxequal_sbert"

    def preference(self, context, query, document1, document2) -> float:
        ranking_data = _preference_vectors(context=context,
                                           document1=document1,
                                           document2=document2,
                                           query=query,
                                           embedding_model=s.SBERT,
                                           comparison_method=s.MEAN,
                                           embedding_style=s.STYLE_AUS_SINGLE_SENTENCE

                                           )
        doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
        doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
        if approximately_equal(doc1_similarity,doc2_similarity):
            return 0
        return strictly_greater(
            doc1_similarity,
            doc2_similarity
        )

    class QArgSim_mean_exact_sbert(Axiom) :
        name = "QArgSim_mean_exact_sbert_targer"

        def preference(self, context, query, document1, document2) -> float :
            ranking_data = _preference_vectors(context=context,
                                               document1=document1,
                                               document2=document2,
                                               query=query,
                                               embedding_model=s.SBERT,
                                               comparison_method=s.MEAN,
                                               embedding_style=s.STYLE_AUS_SINGLE_SENTENCE
                                               )
            doc1_similarity = ranking_data[s.SOCKET_DOCUMENT1]
            doc2_similarity = ranking_data[s.SOCKET_DOCUMENT2]
            return strictly_greater(
                doc1_similarity,
                doc2_similarity
            )