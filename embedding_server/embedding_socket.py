import pandas as pd
import settings as s
import pickle
from loguru import logger
import sys
from embedding_server.embeddings_handler.sbert_embeddings import SBERTEmbeddings
import embedding_server.embeddings_handler.utils_nlp as unlp
import embedding_server.embeddings_handler.utils_targer as ut
from utils.send_data_to_socket import recv_all
import io
import socket
import numpy as np

class EmbeddingsHandler():

    def __init__(self,NLPHandler,path_for_data=None):
        self.cnt = 0
        self.NLPHandler = NLPHandler

        self.stored_data_full_file_path = path_for_data
        if self.stored_data_full_file_path.exists():
            # self.data_df = pd.read_json(self.stored_data_full_file_path,lines=True)
            with open(self.stored_data_full_file_path, 'rb') as file :
                self.data_df = pickle.load(file)
            #self.data_df = pd.read_csv(self.stored_data_full_file_path, sep='\t')
            #self.data_df[s.EMBEDDING] = self.data_df[s.EMBEDDING].apply(lambda x : np.fromstring(x, sep=','))

        else:
            self.data_df = pd.DataFrame()

    def save_embedding(self):
        with open(self.stored_data_full_file_path, 'wb') as f:
            pickle.dump(self.data_df, f)
        #self.data_df[s.EMBEDDING] = self.data_df[s.EMBEDDING].apply(lambda x : np.array2string(x, separator=','))
        #self.data_df.to_csv(self.stored_data_full_file_path, sep='\t', index=False)  # Adjust 'df' if needed
        #self.data_df.to_json(self.stored_data_full_file_path, orient="records", lines=True)

    def get_embedding(self, data_dict):

        dataset_name = data_dict[s.SOCKET_DATASET_KEY]

        docno = data_dict[s.SOCKET_DOCNO]
        document = data_dict[s.SOCKET_DOCUMENT]
        embedding_model = data_dict[s.SOCKET_EMBEDDING_MODEL]

        sentenize = data_dict[s.SOCKET_SENTENICE]
        embedding_style = data_dict[s.SOCKET_EMBEDDING_STYLE]

        task_info = data_dict[s.SOCKET_TASK_INFO]

        if docno is None or document is None or embedding_model is None  or embedding_style is None:
            logger.error('Could not get embedding. Missing arguments.')
            sys.exit(1)
        #
        existing_columns = self.data_df.columns.tolist()
        if len(existing_columns) != 0:
            filtered_df = self.data_df[(self.data_df[s.SOCKET_DATASET_KEY] == dataset_name) &
                                       (self.data_df[s.SOCKET_EMBEDDING_MODEL] == embedding_model) &
                                       (self.data_df[s.SOCKET_EMBEDDING_STYLE] == embedding_style) &
                                       (self.data_df[s.SOCKET_SENTENICE] == sentenize) &  # include extra check for sentenize
                                       (self.data_df[s.SOCKET_DOCNO] == docno)
                                       ]
            if filtered_df.shape[0] == 1 :
                return filtered_df.iloc[0][s.EMBEDDING]
            if filtered_df.shape[0] > 1 :
                raise ValueError(f"More than one embedding found for {docno} with {embedding_model} and {embedding_style} and sentenize {sentenize}")

        # perform embedding
        logger.info(f"Doing Embedding {docno} with {embedding_model} and embedding_style {embedding_style}")
        embedding = self.do_embedding(document=document, embedding_model=embedding_model, embedding_style=embedding_style, sentencing_flag=sentenize, task_info=task_info)
        self.cnt += 1

        data_dict = {s.SOCKET_DATASET_KEY : dataset_name,
                     s.SOCKET_EMBEDDING_MODEL : embedding_model,
                     s.SOCKET_EMBEDDING_STYLE : embedding_style,
                     s.SOCKET_SENTENICE : sentenize,
                     s.SOCKET_DOCNO : docno,
                     s.EMBEDDING : embedding}

        self.data_df = pd.concat([self.data_df, pd.DataFrame([data_dict])], ignore_index=True)
        return embedding

    def lower_sentences(self, sentences):
        assert isinstance(sentences, list)
        sentences_cleaned =  [x.lower() for x in sentences]
        final_annotations = [item for item in sentences_cleaned if item != ""]
        if len(final_annotations) == 0 :
            final_annotations = [" "]
        return final_annotations


    def strip_sentences(self, sentences):
        assert isinstance(sentences, list)
        sentences_cleaned = [x.strip() for x in sentences]
        final_annotations = [item for item in sentences_cleaned if item != ""]
        if len(final_annotations) == 0 :
            final_annotations = [" "]
        return final_annotations

    def do_embedding(self, document=None, embedding_model=None, embedding_style=None, sentencing_flag=True, task_info=None):
        document_data_to_embedd = document
        if isinstance(document,str):
            document_data_to_embedd = [document]

        # strip unnecessary spaces
        document_data_to_embedd = self.strip_sentences(document_data_to_embedd)

        if sentencing_flag:
            document_data_to_embedd = self.NLPHandler.split_sentences(document)

        # make everything lower case
        document_data_to_embedd = self.lower_sentences(document_data_to_embedd)

        if embedding_style in [s.STYLE_AUS_SINGLE_SENTENCE, s.STYLE_AUS_FULL_DOCUMENT]:
            document_data_to_embedd = ut.get_targer_annotation(document_data_to_embedd,task_info)

        # strip unnecessary spaces
        document_data_to_embedd = self.strip_sentences(document_data_to_embedd)
        # document_data_to_embedd = self.lower_sentences(document_data_to_embedd)

        if embedding_model == s.SBERT:
            embedding = SBERTEmbeddings.get_embedding(document_data_to_embedd)
        else:
            raise ValueError(f"Unknown embedding style: {embedding_model}")

        return embedding

# Instantiate Objects
NLPHandler = unlp.TextPreprocessor()
EmbeddHandler = EmbeddingsHandler(NLPHandler,path_for_data=s.AXIOMS_CACHE_EMBEDDINGS_PATH.joinpath('embeddings_data_store.pkl'))


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

        data_requested = None
        if task == s.STMC1:
            data_requested = handle_stmc1(received_data)

        elif task == s.DOCUMENT_RANKING:
            data_requested = handle_document_ranking(received_data)

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

def handle_document_ranking(received_data):

    document1 = received_data[s.SOCKET_DOCUMENT1]
    document2 = received_data[s.SOCKET_DOCUMENT2]
    query = received_data[s.SOCKET_QUERY]

    # queries shall never be converted to AUS, therefore default setting is performed
    query[s.SOCKET_EMBEDDING_STYLE] = s.STYLE_SENTENCES
    query[s.SOCKET_SENTENICE] = False

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

    if comparison == s.MEAN:
        doc1_similarity = np.mean(doc1_similarities_flat)
        doc2_similarity = np.mean(doc2_similarities_flat)

    else:
        raise ValueError(f"Unknown comparison method: {comparison}")

    document1_data = float(doc1_similarity)
    document2_data = float(doc2_similarity)
    return {s.SOCKET_DOCUMENT1 : document1_data , s.SOCKET_DOCUMENT2 : document2_data}




def main():
    # Create a socket

    server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR , 1)

    # Bind to localhost on socket
    server_socket.bind(('localhost' , s.SOCKET_NBR))

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