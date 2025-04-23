# this model is designed to work on the annotated data
import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import matplotlib.pyplot as plt
import settings as s
import utils.get_datafeatures_from_datasets as gdf


# get data needed from dataset, in order to finetune a llama llm
import pyterrier as pt
from pyterrier.datasets import get_dataset
import utils.get_datafeatures_from_datasets as gdf
if not pt.java.started() :
    pt.java.init()
import settings as s
import json
from collections import defaultdict
def get_used_dataset_from_index(dataset_name):
    print(f"Getting data for {dataset_name}")

    # get all human annotated qrels
    s.set_data_manually(dataset_name)

    # dataset = get_dataset(f'irds:{s.dataset}')
    # data_qrels = dataset.get_qrels()
    # queries = dataset.get_topics()

    indexref = pt.IndexRef.of(str(s.dataset_index_dir))
    index = pt.IndexFactory.of(indexref)
    meta = index.getMetaIndex()

    all_content_list = []

    # Get document IDs and iterate
    for docid in range(index.getCollectionStatistics().getNumberOfDocuments()) :
        docno = meta.getItem("docno", docid)
        print(f"DocID: {docid}, Docno: {docno}")
        # You can also get the full text if stored
        content = meta.getItem("text", docid)

        document_dict = {}
        document_dict["docid"] = docid
        document_dict["docno"] = docno
        document_dict["text"] = content
        all_content_list.append(document_dict)


    # File path for the JSONL file

    # Open the file in write mode
    with open(s.PATH_TOUCHE_21_FROM_INDEX_JSON, 'w') as file :
        for item in all_content_list :
            file.write(json.dumps(item) + '\n')

if __name__ == '__main__' :
    touche_21_data = get_used_dataset_from_index('touche21')
