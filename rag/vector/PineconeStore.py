from rag.vector.BaseVectorStore import BaseVectorStore
from rag.vector.PineconeUtils import PineconeUtils


class PineconeStore(BaseVectorStore):
    util: PineconeUtils

    def __init__(self, key: str):
        self.util = PineconeUtils(key=key)

    def insert(self, vectors: list[float], content: str, **param) -> bool:
        index_name = param["index_name"]
        index = self.util.getOrCreateIndex(index_name=index_name)
        id_name = param["id_name"]
        value_key = param["value_key"]
        self.util.upsertVectors(index=index, vectors=[(id_name, vectors, {value_key: content})])
        return True

    def query(self, question_vectors: list[float], **param):
        index_name = param["index_name"]
        index = self.util.getOrCreateIndex(index_name=index_name)
        vector_results = self.util.queryByVectors(vectors=question_vectors, index=index, top_k=1)
        print(vector_results)
        return vector_results[0].vectors, vector_results[0].metadata
