import sys

import requests
import settings as s
from typing import Tuple, AnyStr, Any
import numpy as np
import base64
import pickle
from utils.send_data_to_socket import send_data_to_socket

def transmission_dict(id=None, document=None, embedding_model=None, embedding_style=None, sentenice=None, task=None, task_info=None):

    required_args = {
        "id" : id,
        "document" : document,
        "embedding_model" : embedding_model,
        "embedding_style" : embedding_style,
        "sentenice" : sentenice,
        "task" : task,
    }

    missing = [k for k, v in required_args.items() if v is None]
    if missing :
        raise ValueError(f"Missing required arguments: {', '.join(missing)}")

    data = {
        s.SOCKET_DOCNO : id ,
        s.SOCKET_DOCUMENT : document ,
        s.SOCKET_EMBEDDING_MODEL : embedding_model,
        s.SOCKET_EMBEDDING_STYLE : embedding_style,
        s.SOCKET_SENTENICE : sentenice,
        s.SOCKET_TASK : task,
        s.SOCKET_TASK_INFO : task_info,
        s.SOCKET_DATASET_KEY : s.DATASET_NAME_SHORT
    }
    return data


def document_ranking_socket_sent(document1_data=None , document2_data=None , query_data=None , comparison=None,task=None):
    if task is None:
        sys.exit("Task is not defined")

    data = {
        s.SOCKET_DOCUMENT1 : document1_data,
        s.SOCKET_DOCUMENT2 : document2_data,
        s.SOCKET_QUERY : query_data,
        s.SOCKET_COMPARE_METHOD : comparison,
        s.TASK : task
    }
    result = send_data_to_socket(data)
    return result


def get_search_contents(context, document1, document2, query_text) -> Tuple[AnyStr,AnyStr,AnyStr]:
    doc1_text = context.document_contents(document1)
    doc2_text = context.document_contents(document2)
    query_text = query_text.title
    return doc1_text , doc2_text, query_text


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

def _preference_vectors(context=None, document1=None, document2=None, query=None, embedding_model = None, comparison_method=None, document_sentenice=None, embedding_style=None, task=None, task_info=None) -> Tuple[Any,Any,Any]:

    required_args = {
        "context" : context,
        "document1" : document1,
        "document2" : document2,
        "query" : query,
        "embedding_model" : embedding_model,
        "comparison_method" : comparison_method,
        "document_sentenice" : document_sentenice,
        "embedding_style" : embedding_style,
        "task" : task,
    }

    missing = [k for k, v in required_args.items() if v is None]
    if missing :
        raise ValueError(f"Missing required arguments: {', '.join(missing)}")

    document1_text,document2_text,query_text = get_search_contents(context, document1, document2, query)

    doc1_vectors = transmission_dict(id=document1.id,
                                     document=document1_text,
                                     embedding_model=embedding_model,
                                     embedding_style=embedding_style,
                                     sentenice=document_sentenice,
                                     task=task,
                                     task_info=task_info)

    doc2_vectors = transmission_dict(id=document2.id,
                                     document=document2_text,
                                     embedding_model=embedding_model,
                                     embedding_style=embedding_style,
                                     sentenice=document_sentenice,
                                     task=task,
                                     task_info=task_info)

    # the query shall never be split into AUS
    query_vector = transmission_dict(id=query_text,
                                     document=query_text,
                                     embedding_model=embedding_model,
                                     embedding_style=embedding_style,
                                     sentenice=False,
                                     task=task,
                                     task_info=task_info)

    ranking_data = document_ranking_socket_sent(document1_data=doc1_vectors,
                                                document2_data=doc2_vectors,
                                                query_data=query_vector,
                                                comparison=comparison_method,
                                                task=task)
    return ranking_data


