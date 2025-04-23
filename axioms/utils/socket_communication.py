import sys

import requests
import settings as s
from typing import Tuple, AnyStr, Any
import numpy as np
import base64
import pickle
from utils.send_data_to_socket import send_data_to_socket

def transmission_dict(id=None, document=None, embedding_model=None, sentenize=None, task=None, embedding_style=None, task_info=None):
    data = {
        s.SOCKET_DOCNO : id ,
        s.SOCKET_DOCUMENT : document ,
        s.SOCKET_EMBEDDING_MODEL : embedding_model,
        s.SOCKET_SENTENIZE : sentenize,
        s.SOCKET_TASK : task,
        s.SOCKET_EMBEDDING_STYLE : embedding_style,
        s.SOCKET_TASK_INFO : task_info
    }
    return data


def document_ranking_socket_sent(document1_data , document2_data , query_data , comparison,task=None):
    if task is None:
        #sys.exit("Task is not defined")
        #print("Task is not defined")
        task = s.DOCUMENT_RANKING
    data = {
        s.TASK : task,
        s.SOCKET_DOCUMENT1 : document1_data,
        s.SOCKET_DOCUMENT2 : document2_data,
        s.SOCKET_QUERY : query_data,
        s.SOCKET_COMPARE_METHOD : comparison,
        s.SOCKET_DATASET_KEY : s.dataset_name_short
    }
    result = send_data_to_socket(data)
    return result

# def sent_embedding_request(id=None , document=None , embedding_style=None , sentence_style =None , sentenize=None):
#
#     data = transmission_dict(id=id, document=document, embedding_model=embedding_style, sentence_style =sentence_style, sentenize=sentenize)
#
#     response = send_data_to_socket(data)
#     if response.status_code == 200 :
#         print("Embedding:" , response.json()['embedding'])
#         return response.json()['embedding']
#     else :
#         try:
#             print("Error:" , response.json()['error'])
#         except requests.exceptions.JSONDecodeError:
#             print("Error: No response from server")
#         return None


# def get_embedding_socket(id=None , document=None , embedding_style=None , sentence_style =None , sentenize=None):
#     data = transmission_dict(id=id, document=document, embedding_model=embedding_style, sentence_style =sentence_style, sentenize=sentenize, task=s.EMBEDD_SINGLE)
#     result = send_data_to_socket(data)
#     return result



def get_search_contents(context, document1, document2, query) -> Tuple[AnyStr,AnyStr,AnyStr]:
    doc1_text = context.document_contents(document1)
    doc2_text = context.document_contents(document2)
    query = query.title
    return doc1_text , doc2_text,query


def deserialize_embedding(data_deserialized):

    list_to_return = []

    assert len(data_deserialized['shape']) == len(data_deserialized['dtype']) == len(data_deserialized['data'])

    for i in range(0, len(data_deserialized['shape'])):
        shape = tuple(data_deserialized['shape'][i])
        dtype = data_deserialized['dtype'][i]
        data = base64.b64decode(data_deserialized['data'][i])
        arr = np.frombuffer(data , dtype=dtype).reshape(shape)
        list_to_return.append(arr)
    return list_to_return

def _preference_vectors(context=None , document1=None , document2=None , query=None  , embedding_style = None , document_sentenice= True, comparison_method=None , task_socket=None , identifier=None , task_info=None) -> Tuple[Any,Any,Any]:

    document1_text,document2_text,query_text = get_search_contents(context, document1, document2, query)

    doc1_vectors = transmission_dict(id=document1.id, document=document1_text, embedding_model=embedding_style, sentenize=document_sentenice, embedding_style=identifier, task_info=task_info)
    doc2_vectors = transmission_dict(id=document2.id, document=document2_text, embedding_model=embedding_style, sentenize=document_sentenice, embedding_style=identifier, task_info=task_info)

    # the query shall never be split into AUS
    query_vector = transmission_dict(id=query_text, document=query_text, embedding_model=embedding_style, sentenize=False, embedding_style=identifier, task_info=task_info)

    ranking_data = document_ranking_socket_sent(doc1_vectors , doc2_vectors , query_vector , comparison_method , task_socket)
    return ranking_data


if __name__ == "__main__":

    x = sent_embedding_request(id="123", document="Some text to embed. Evenmore things to embedd.", embedding_style=s.SBERT, sentence_style=s.sentences, sentenize=True)
    x_de = deserialize_embedding(x)
    def dump_data(data , name) :
        with open(s.root / name , 'wb') as file :
            pickle.dump(data , file)
    dump_data(x_de , 'client.pkl')
    print(x_de)