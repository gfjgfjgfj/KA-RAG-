from sentence_transformers import SentenceTransformer

from rag.vector.base_api import Api


class LibraryVectorUtil:
    def __init__(self):
        self.api = Api(ip="http://localhost:8882")
        # self.api = Api()
        self.embedding = SentenceTransformer('BAAI/bge-large-zh-v1.5')

    def str2vectors(self, text):
        return self.embedding.encode(sentences=text, normalize_embeddings=True).tolist()

    def create_index(self, index_name):
        return self.api.isSuccess(self.api.post(interface="create_vector_index", body={"index_name": index_name}))

    def check_index(self, index_name):
        return self.api.getData(self.api.post(interface="check_index", body={"index_name": index_name}))
    def insert_vector(self, index_name, text):
        print("向量化")
        vectors = self.str2vectors(text)
        body = {"index_name": index_name, "vectors": vectors, "text": text}
        print(body)
        return self.api.isSuccess(self.api.post(interface="upload", body={"index_name": index_name, "vectors": vectors, "text": text}))

    def query(self, index_name, query, top_k=1):
        vectors = self.str2vectors(query)
        return self.api.post(interface="query_vector", body={"index_name": index_name, "vectors": vectors, "top_k": top_k})

    def delete(self, index_name, id):
        return self.api.isSuccess(self.api.post(interface="delete", body={"index_name": index_name, "id": id}))

    def query_result_translate(self, result):
        try:
            print(result)
            data = self.api.getData(response=result)
            print(data)
            obj = data['hits']['hits']
            print(obj)
            result = []
            for item in obj:
                result.append(item['_source']['text'])
            re = "\n".join(result)
            return re
        except Exception as e:
            print(e)
            return None
