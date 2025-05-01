import pickle

import numpy as np

import embedding_server.embeddings_handler.utils_nlp as unlp
import embedding_server.embedding_socket as es
import settings as s


#  SBERT Retriever for Touche-21 Dataset, based on logic of the used axioms
class SBERTRanker() :
    def __init__(self) :
        self.dataset_name = 'touche21'
        NLPHandler = unlp.TextPreprocessor()
        self.EmbeddingHandler = es.EmbeddingsHandler(NLPHandler,
                                                     path_for_data=s.STORAGE_SBERT_EMBEDDINGS_SBERT_RANKER_PKL_DATA)

    def go_embeddings_single_sentence_document(self) :
        final_data_list = []
        with open(s.PATH_TOUCHE_21_FROM_INDEX_PKL_DATA, 'rb') as file :
            data_for_embedding = pickle.load(file)

        queries = data_for_embedding['queries']
        data_qrels = data_for_embedding['data_qrels']
        docnos_dict = data_for_embedding['docnos']

        qids = data_qrels['qid'].unique()
        for qid in qids :

            # filter qrels df to corresponding qid, so we have only considered docnos
            data_qrels_single_qid = data_qrels[data_qrels['qid'] == qid]
            query = queries[queries['qid'] == qid]["query"].values[0]

            socket_query_data_dict = {
                s.SOCKET_DATASET_KEY : self.dataset_name,
                s.SOCKET_DOCUMENT : query,
                s.SOCKET_DOCNO : query,
                s.SOCKET_EMBEDDING_MODEL : s.SBERT,
                s.SOCKET_EMBEDDING_STYLE : s.STYLE_SENTENCES,
                s.SOCKET_SENTENICE : False,
                s.SOCKET_TASK_INFO : ""
            }

            query_embedding = self.EmbeddingHandler.get_embedding(socket_query_data_dict)

            document_embeddings = []
            for i, row in data_qrels_single_qid.iterrows() :

                row_dict = row.to_dict()
                docno = row_dict['docno']
                qid = row_dict['qid']

                if docno not in docnos_dict :
                    print(f"Document {docno} not in index")
                    continue
                document = docnos_dict[docno]

                socket_document_data_dict = {
                    s.SOCKET_DATASET_KEY : self.dataset_name,
                    s.SOCKET_DOCUMENT : document,
                    s.SOCKET_DOCNO : docno,
                    s.SOCKET_EMBEDDING_MODEL : s.SBERT,
                    s.SOCKET_EMBEDDING_STYLE : s.STYLE_SENTENCES,
                    s.SOCKET_SENTENICE : True,  # we convert the model
                    s.SOCKET_TASK_INFO : ""
                }

                document_embedding = self.EmbeddingHandler.get_embedding(socket_document_data_dict)
                document_embeddings.append((document_embedding, docno))

            similiarity_list = []
            for document_embedding, docno in document_embeddings :
                max_sentence_raw = np.dot(document_embedding, query_embedding.T)
                max_sentence = float(np.max(max_sentence_raw))
                similiarity_list.append((max_sentence, docno))

            # create ranking of the retrieved documents based on similiarity
            similiarity_list = sorted(similiarity_list, key=lambda x: x[0], reverse=True)

            # convert results to dataframe following TREC FORMAT
            for i, (sim, docno) in enumerate(similiarity_list) :
                rank = i + 1
                final_data_string = f"{qid} Q0 {docno} {rank} {sim} SBERT-SINGLE-SENTENCE-MAX"
                final_data_list.append(final_data_string)

            self.EmbeddingHandler.save_embedding()

        with open("SBERT-SINGLE-SENTENCE-MAX.txt", 'w') as file :
            for line in final_data_list :
                file.write(line + "\n")


if __name__ == '__main__' :
    sbert_ranker = SBERTRanker()
    sbert_ranker.go_embeddings_single_sentence_document()