# this model is designed to work on the annotated data
import pyterrier as pt
if not pt.java.started() :
    pt.java.init()
import matplotlib.pyplot as plt
import settings as s
import utils.get_datafeatures_from_datasets as gdf
import json
import os

# create BERT BASELINE FOR BETTER DATA PROCESSING
class SBERTRanker():
    def __init__(self, model_name, data):

        self.model_name = model_name
        self.data = data
        self.model = None
        self.embeddings = None
        self.ranking = None
        self.ranked_data = None
        self.load_model()
        self.create_embeddings()
        self.rank_data()

        s.set_data_manually('touche21')

    def load_json(self, data) :
        # Get file extension
        _, ext = os.path.splitext(data)

        with open(data, 'r', encoding='utf-8') as file :
            if ext.lower() == '.jsonl' :
                # Each line is a separate JSON object
                parsed_data = [json.loads(line) for line in file if line.strip()]
            elif ext.lower() == '.json' :
                # Load entire JSON file (can be a list or dict)
                parsed_data = json.load(file)
                # If it's a dict, wrap it in a list to keep DataFrame consistency
                if isinstance(parsed_data, dict) :
                    parsed_data = [parsed_data]
            else :
                raise ValueError("Unsupported file format. Please use .json or .jsonl")

        return parsed_data

    # cycle through the underlying json l
    def do_embeddings_full_document(self):
        # Load the JSON data


        experiment_name = 'dirichletlm-baseline-reranking-touche21-top10-human-eval'

        indexref = pt.IndexRef.of(str(s.dataset_index_dir))
        index = pt.IndexFactory.of(indexref)
        stat = index.getCollectionStatistics()

        rerank_nbr = 10  # number of documents to rerank

        queries = gdf.get_dataset_queries()


class SBERTSentenceRanker():
    def __init__(self, model_name, data):
        self.model_name = model_name
        self.data = data
        self.model = None
        self.embeddings = None
        self.ranking = None
        self.ranked_data = None
        self.load_model()
        self.create_embeddings()
        self.rank_data()

        s.set_data_manually('touche21')

        experiment_name = 'dirichletlm-baseline-reranking-touche21-top10-human-eval'

        indexref = pt.IndexRef.of(str(s.dataset_index_dir))
        index = pt.IndexFactory.of(indexref)
        stat = index.getCollectionStatistics()

        rerank_nbr = 10  # number of documents to rerank

        queries = gdf.get_dataset_queries()