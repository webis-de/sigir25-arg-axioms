import os
import shutil

import pyterrier as pt
from loguru import logger

import settings as s

if not pt.java.started():
    pt.java.init()

from pyterrier.datasets import get_dataset


class IndexData:
    def __init__(self, dataset):

        self.docnos_to_ignore = set()
        self.dataset = dataset


    # idea of filtering, negative caveat that the size of the index is massively reduced
    def generate_filter_qrels(self) :
        for d in DATASET.get_corpus_iter() :
            if (d['docno'] in docnos_qrels) : # qrel filtering happens on side of the participants
                if not isinstance(d['premises_texts'],str):
                    logger.warning(f"Document {d['docno']} has no premises_texts")
            yield {'docno' : d['docno'] , 'text' : d['premises_texts']}


    def generate_filter_minimal_length(self):
        index_docnos_set = set() # set of docnos to prevent duplicates
        total_cnt = 0
        indexed_cnt = 0
        max_length_text = 0
        max_length_title = 0
        empty_docs = 0
        for d in self.dataset.get_corpus_iter() :
            total_cnt += 1
            docno = d['docno']
            if (docno in self.docnos_to_ignore) or (docno in index_docnos_set):
                continue
            if len(d['text']) == 0 :
                empty_docs += 1
                continue
            if len(d['text'])  >= 30: # filter out very short documents
                index_docnos_set.add(d['docno'])
                indexed_cnt += 1
                if len(d['text']) > max_length_text:
                        max_length_text = len(d['text'])
                if len(d['title']) > max_length_title:
                    max_length_title = len(d['title'])
                yield {'docno' : d['docno'] , 'text' : d['text'], 'title': d['title']}

        print(f"Indexing finished. Overview of the dataset:")
        print(f"{max_length_text} is the maximum length of a document.")
        print(f"{max_length_title} is the maximum length of a title.")
        print(f"{empty_docs} documents have no premises_texts.")
        print(f"{indexed_cnt} documents were indexed.")
        print(f"{total_cnt} documents were processed.")
        print('docnos set', len(index_docnos_set))

    def do_indexing_control(self): # iterate over the raw index and drop documents that contain no tokens
        self.do_indexing() # first indexing
        self.index_find_empty_tokens() # then iterate over the index and notate entries with empty tokens
        self.do_indexing() # second indexing

    def index_find_empty_tokens(self): # iterate over index and notate entries with empty tokens
        indexref = pt.IndexRef.of(str(s.DATASET_INDEX_DIR))
        index = pt.IndexFactory.of(indexref)
        iter = index.get_corpus_iter()
        for x in iter:
            tokens = x['toks']
            docno = x['docno']
            if len(tokens) == 0:
                self.docnos_to_ignore.add(docno)
        print(f"Found {len(self.docnos_to_ignore)} documents with empty tokens.")
        for docno in self.docnos_to_ignore:
            print(docno)

    def delete_directory(self,path) :
        if os.path.exists(path) :
            shutil.rmtree(path)
            print(f"Directory '{path}' and all its contents have been deleted.")
        else :
            print(f"Directory '{path}' does not exist.")

    def do_indexing(self): # sort out very short documents or strange documents with no tokens
        if s.DATASET_INDEX_DIR.exists():
            self.delete_directory(s.DATASET_INDEX_DIR)

        indexer = pt.terrier.IterDictIndexer( # we have to do an adjusting of the corresponding fields
            str(s.DATASET_INDEX_DIR), meta={'docno': 100, 'text': 110000, 'title': 1200}, fields=True
            )
        indexer.index(self.generate_filter_minimal_length())


if __name__ == '__main__':
    s.set_data_manually('touche20')
    dataset_name = 'beir/webis-touche2020/v2'
    DATASET = get_dataset(f'irds:{dataset_name}')

    # get qrels and docno of documents, which have a relevance judgment
    qrels = DATASET.get_qrels()
    topics = DATASET.get_topics()
    documents = DATASET.get_corpus_iter()
    dc_cnt = 0
    for x in documents:
        dc_cnt += 1

    docnos_qrels = qrels['docno'].values
    nbr_of_qrels = len(docnos_qrels)
    nbr_of_documents = len(documents)
    print(f"Initial count")
    print(f"Number of qrels: {nbr_of_qrels}")
    print(f"Number of documents: {dc_cnt}")

    index_data = IndexData(DATASET)
    index_data.do_indexing_control()

