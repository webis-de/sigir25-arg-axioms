
import numpy as np
from numpy import mean
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

# obtain necessary SBERT embeddings
class SBERTEmbeddings:

    model = SentenceTransformer('all-mpnet-base-v2')
    @staticmethod
    def get_embedding(text) :
        if not isinstance(text , list) :
            text = [text]
        embedding = SBERTEmbeddings.model.encode(text)
        return embedding

if __name__ == '__main__':
    Embedder = SBERTEmbeddings()

    text = ['Hello there.', 'General Kenobi.', 'hello there.']
    query = ['Obi Wan.']
    embeddings = Embedder.get_embedding(text)
    query_embedding = Embedder.get_embedding(query)

    doc1_similarity = [cosine_similarity(query_embedding , vector.reshape(1 , -1)) for vector in embeddings]
    doc1_similarity_alter = util.cos_sim(query_embedding , embeddings)

    doc1_similarity_faster = np.dot(embeddings , query_embedding.T)
    doc1_similarity_faster_mean = mean(doc1_similarity_faster)
    doc1_similarity_mean = mean([cosine_similarity(query_embedding , vector.reshape(1 , -1)) for vector in embeddings])
    mewo = 1