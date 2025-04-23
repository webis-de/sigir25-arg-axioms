import settings as s
import pickle
from loguru import logger
import sys
from nlp_server.embeddings_handler.ada_embeddings import AdaEmbeddings
from nlp_server.embeddings_handler.sbert_embeddings import SbertEmbeddings
import nlp_server.embeddings_handler.utils_nlp as unlp
import nlp_server.embeddings_handler.utils_targer as ut
from utils.send_data_to_socket import recv_all
import io
import socket
import numpy as np

class EmbeddingsHandler():

    def __init__(self,NLPHandler):
        self.cnt = 0
        self.NLPHandler = NLPHandler

        if not s.AXIOMS_CACHE_EMBEDDINGS_PATH.exists():
            s.AXIOMS_CACHE_EMBEDDINGS_PATH.mkdir(parents=True)

        self.stored_data_full_file_path = s.AXIOMS_CACHE_EMBEDDINGS_PATH.joinpath('embeddings_data_store.json')
        if self.stored_data_full_file_path.exists():
            with open(self.stored_data_full_file_path, 'rb') as file:
                self.data = pickle.load(file)
        else:
            self.data = {}

        self.data_current_dataset = self.data

    def save_embedding(self):
        with open(self.stored_data_full_file_path, 'wb') as file:
            pickle.dump(self.data, file)

    def get_embedding(self, data_dict):
        docno = data_dict[s.SOCKET_DOCNO]
        document = data_dict[s.SOCKET_DOCUMENT]
        embedding_model = data_dict[s.SOCKET_EMBEDDING_MODEL]

        sentenize = data_dict[s.SOCKET_SENTENIZE]
        task = data_dict[s.SOCKET_TASK]
        embedding_style = data_dict[s.SOCKET_EMBEDDING_STYLE]
        task_info = data_dict[s.SOCKET_TASK_INFO]

        if docno is None or document is None or embedding_model is None  or embedding_style is None:
            logger.error('Could not get embedding. Missing arguments.')
            sys.exit(1)

        if embedding_style not in self.data_current_dataset:
            self.data_current_dataset[embedding_style] = {s.SBERT: dict()}

        embed_data_dict = self.data_current_dataset[embedding_style][embedding_model]

        if docno in embed_data_dict:
            return embed_data_dict[docno]
        else:
            # perform embedding
            logger.info(f"Doing Embedding {docno} with {embedding_model} and embedding_style {embedding_style}")
            embedding = self.do_embedding(document=document, embedding_style=embedding_model, identifier=embedding_style, sentencing_flag=sentenize, task_info=task_info)
            self.cnt += 1
            embed_data_dict.update({docno: embedding})
            return embedding

    def clean_sentences(self,sentences):
        sentences_cleaned =  [x.lower().strip() for x in sentences]
        final_annotations = [item for item in sentences_cleaned if item != ""]
        if len(final_annotations) == 0 :
            final_annotations = [" "]
        return final_annotations

    def do_embedding(self, document=None, embedding_style=None, identifier=None, sentencing_flag=True, task_info=None):
        document_data_to_embedd = document
        if isinstance(document,str):
            document_data_to_embedd = [document]

        if sentencing_flag:
            document_data_to_embedd = self.NLPHandler.create_sentences(document)

        document_data_to_embedd = self.clean_sentences(document_data_to_embedd) # basic cleaning, which is always done

        if identifier in [s.IDENT_AUS_SINGLE_SENTENCE, s.IDENT_AUS_FULL_DOCUMENT]:
            document_data_to_embedd = ut.get_targer_annotation(document_data_to_embedd,task_info)

        if embedding_style == s.SBERT:
            embedding = SbertEmbeddings.get_embedding(document_data_to_embedd)
        # if embedding_style == s.ADA:
        #     embedding = AdaEmbeddings.get_embedding(document_data_to_embedd)
        else:
            raise ValueError(f"Unknown embedding style: {embedding_style}")

        return embedding

# Instantiate Objects
NLPHandler = unlp.TextPreprocessor()
EmbeddHandler = EmbeddingsHandler(NLPHandler)


def handle_client(connection):
    try:
        # Receive the length of the incoming data (4 bytes)
        data_length = int.from_bytes(connection.recv(4), 'big')

        # Receive the actual pickled data based on the length
        pickled_data = recv_all(connection , data_length)

        # Create a memory buffer and load the pickled data from it
        memory_buffer = io.BytesIO(pickled_data)
        memory_buffer.seek(0)

        # Unpickle the data
        received_data = pickle.load(memory_buffer)

        # the received data contains the task and further information
        task = received_data[s.TASK]

        dataset_name = received_data[s.SOCKET_DATASET_KEY]
        if dataset_name not in EmbeddHandler.data:
            EmbeddHandler.data[dataset_name] = dict()

        # set the corresponding data for calculation
        EmbeddHandler.data_current_dataset = EmbeddHandler.data[dataset_name]

        data_requested = None
        if task == s.SMTC1:
            data_requested = handle_stmc1(received_data)
        # elif task == s.BATCH_EMBEDDING:
        #     data_requested = handle_embedding_batch(received_data)
        elif task == s.DOCUMENT_RANKING:
            data_requested = handle_document_ranking(received_data)
        # elif task == s.TARGER_ANALYSIS:
        #     data_requested = handle_targer_analysis(received_data)
        else:
            raise ValueError(f"Unknown task: {task}")

        if EmbeddHandler.cnt != 0:
            EmbeddHandler.cnt = 0
            EmbeddHandler.save_embedding()

        # Create a response data dictionary
        response_data = {'status' : s.OK , 'data' : data_requested}

        # Create an in-memory bytes buffer and pickle the response data
        response_buffer = io.BytesIO()
        pickle.dump(response_data, response_buffer)

        # Reset buffer to the beginning
        response_buffer.seek(0)

        # Convert memory buffer to bytes for sending
        pickled_response = response_buffer.read()

        # Send the length of the pickled response data first
        connection.sendall(len(pickled_response).to_bytes(4 , 'big'))

        # Send the actual pickled response data
        connection.sendall(pickled_response)

    finally :
        # Close the client connection
        connection.close()

# def handle_targer_analysis(received_data):
#     docnos = received_data[s.docnos]
#     documents = received_data[s.texts]
#
#     documents_in_sentences = []
#     documents_in_arguments = []
#     for i,x in enumerate(documents):
#         percentage = (i + 1) / len(documents) * 100
#         print(f"Progress: {percentage:.2f}% sentence {i+1} of {len(documents)}")
#
#         sentences = EmbeddHandler.NLPHandler.create_sentences(x)
#         sentences = [x.lower() for x in sentences]
#
#         sentences_targer = ut.get_targer_annotation(sentences)
#         documents_in_sentences.append(sentences)
#         documents_in_arguments.append(sentences_targer)
#     data = {s.sentences : documents_in_sentences , s.argument_units :  documents_in_arguments}
#     return data

# def handle_embedding_batch(received_data):
#     docnos = received_data[s.docnos]
#     documents = received_data[s.texts]
#     assert len(docnos) == len(documents)
#
#     for embedding_style in s.EMBDEDDINGS_STYLES:
#         for sentence_style in s.SENTENCE_STYLES:
#             for i in range(0, len(docnos)):
#                 id = docnos[i]
#                 document = documents[i]
#                 embedding = EmbeddHandler.get_embedding(id , document , embedding_style , sentence_style , True)
#     return None
#         #embeddings.append(embedding)
#    # return embeddings

def handle_document_ranking(received_data):
    document1 = received_data[s.SOCKET_DOCUMENT1]
    document2 = received_data[s.SOCKET_DOCUMENT2]
    query = received_data[s.SOCKET_QUERY]

    # queries shall never be converted to AUS, therefore default setting is performed
    query[s.SOCKET_EMBEDDING_STYLE] = s.IDENT_SENTENCES
    query[s.SOCKET_SENTENIZE] = False

    comparison = received_data[s.SOCKET_COMPARE_METHOD]

    document1_embedding = EmbeddHandler.get_embedding(document1)
    document2_embedding = EmbeddHandler.get_embedding(document2)
    query_embedding = EmbeddHandler.get_embedding(query)

    doc1_similarity = np.dot(document1_embedding , query_embedding.T)
    doc2_similarity = np.dot(document2_embedding , query_embedding.T)

    if comparison == s.MAX:
        doc1_similarity = np.max(doc1_similarity)
        doc2_similarity = np.max(doc2_similarity)
    if comparison == s.MEAN:
        doc1_similarity = np.mean(doc1_similarity)
        doc2_similarity = np.mean(doc2_similarity)

    document1_data = float(doc1_similarity)
    document2_data = float(doc2_similarity)
    return {s.SOCKET_DOCUMENT1 : document1_data , s.SOCKET_DOCUMENT2 : document2_data}

def handle_stmc1(received_data):
    document1 = received_data[s.SOCKET_DOCUMENT1]
    document2 = received_data[s.SOCKET_DOCUMENT2]
    query = received_data[s.SOCKET_QUERY]
    comparison = received_data[s.SOCKET_COMPARE_METHOD]

    document1_embeddings = EmbeddHandler.get_embedding(document1)
    document2_embeddings = EmbeddHandler.get_embedding(document2)
    query_embedding = EmbeddHandler.get_embedding(query)

    doc1_similarities = np.dot(document1_embeddings , query_embedding.T)
    doc2_similarities = np.dot(document2_embeddings , query_embedding.T)

    doc1_similarities_flat = doc1_similarities.flatten()  # 1D array of shape (num_docs1 * num_queries,)
    doc2_similarities_flat = doc2_similarities.flatten()


    if comparison == s.MAX:
        doc1_similarity = np.max(doc1_similarities_flat)
        doc2_similarity = np.max(doc2_similarities_flat)
    if comparison == s.MEAN:
        doc1_similarity = np.mean(doc1_similarities_flat)
        doc2_similarity = np.mean(doc2_similarities_flat)

    document1_data = float(doc1_similarity)
    document2_data = float(doc2_similarity)
    return {s.SOCKET_DOCUMENT1 : document1_data , s.SOCKET_DOCUMENT2 : document2_data}




def main():
    # Create a socket

    server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

    # Bind to localhost on socket
    server_socket.bind(('localhost' , s.server_port))

    # Listen for incoming connections
    server_socket.listen(1)
    print("Server is waiting for connections...")

    try :
        while True :
            # Accept a connection
            connection , client_address = server_socket.accept()
            print(f"Connection established with {client_address}")

            # Handle the client in a separate function
            handle_client(connection)

    except KeyboardInterrupt :
        print("Server is shutting down.")
    finally :
        # Close the server socket
        server_socket.close()




if __name__ == '__main__':
    main()