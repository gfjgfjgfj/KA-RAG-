from typing import Iterable, List, Type, Union, Optional

import numpy as np
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import CharacterTextSplitter
from numpy._typing import NDArray
from pinecone import Pinecone, ServerlessSpec, Index

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader

Vector = NDArray[Union[np.int32, np.float32]]

class QueryResultBean:
    score: float = 0.0
    id: str = ""
    vectors: [float] = []
    metadata: [str] = []


class PineconeUtils:
    pinecone: Pinecone

    def __init__(self, key: str):
        self.pinecone = Pinecone(api_key=key)

    def getOrCreateIndex(
            self,
            index_name: str,
            dimension: int = 768,
            cloud: str = "aws",
            regin: str = "us-east-1"
    ) -> Index:
        if not self.indexIsExist(index_name):
            self.pinecone.create_index(
                name=index_name,
                dimension=dimension,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=regin
                )
            )
        return self.pinecone.Index(index_name)

    def indexIsExist(self, index_name: str) -> bool:
        for it in self.pinecone.list_indexes():
            if it["name"] == index_name:
                return True
        return False

    def upsertFromDocument(
            self,
            index: Index,
            documents: List[Document],
            embeddings: Embeddings,
            id_name: str,
            value_key: str = "text"
    ):
        for i, text in enumerate(documents):
            vector = embeddings.embed_query(text.page_content)
            index.upsert([(f"{id_name}_{i}", vector, {value_key: text.page_content})])

    def upsertFromLoader(
            self,
            index: Index,
            loader: BaseLoader,
            embeddings: Embeddings,
            id_name: str,
            value_key: str = "text"
    ):
        documents = loader.load()
        self.upsertFromDocument(index=index, documents=documents, embeddings=embeddings, id_name=id_name,
                                value_key=value_key)

    def upsertFromFile(
            self,
            index: Index,
            filePath: str,
            embeddings: Embeddings,
            id_name: str,
            value_key: str = "text"
    ):
        if filePath.endswith('.pdf'):
            self.upsertFromLoader(index=index, loader=PyPDFLoader(file_path=filePath), embeddings=embeddings,
                                  id_name=id_name,
                                  value_key=value_key)
        elif filePath.endswith('.docx'):
            self.upsertFromLoader(index=index, loader=Docx2txtLoader(file_path=filePath), embeddings=embeddings,
                                  id_name=id_name,
                                  value_key=value_key)
        elif filePath.endswith('.txt'):
            self.upsertFromLoader(index=index, loader=TextLoader(file_path=filePath), embeddings=embeddings,
                                  id_name=id_name,
                                  value_key=value_key)

    def upsertVectors(
            self,
            index: Index,
            vectors: Union[List[Vector], List[tuple], List[dict]],
            namespace: Optional[str] = None,
    ):
        index.upsert(vectors=vectors, namespace=namespace)

    def query(
            self,
            obj: str,
            index: Index,
            embeddings: Embeddings,
            top_k: int = 10,
            metadata_key: str = "text",
            include_values: bool = False,
            include_metadata: bool = True
    ) -> List[QueryResultBean]:

        query_vector = embeddings.embed_query(obj)
        results = index.query(vector=query_vector, top_k=top_k, include_metadata=include_metadata,
                              include_values=include_values)
        re = []
        print(results)
        for it in results["matches"]:
            bean = QueryResultBean()
            if include_values:
                bean.vectors = it["values"]
            if include_metadata:
                bean.metadata = it["metadata"][metadata_key]
            bean.score = it["score"]
            bean.id = it["id"]
            re.append(bean)
        return re

    def queryByVectors(
            self,
            vectors: List[float],
            index: Index,
            top_k: int = 10,
            metadata_key: str = "text",
            include_values: bool = False,
            include_metadata: bool = True
    ) -> List[QueryResultBean]:

        results = index.query(vector=vectors, top_k=top_k, include_metadata=include_metadata,
                              include_values=include_values)
        re = []
        print(results)
        for it in results["matches"]:
            bean = QueryResultBean()
            if include_values:
                bean.vectors = it["values"]
            if include_metadata:
                bean.metadata = it["metadata"][metadata_key]
            bean.score = it["score"]
            bean.id = it["id"]
            re.append(bean)
        return re

    def splitDocument(
            self,
            documents: Iterable[Document],
            chunk_size: int = 500,
            chunk_overlap: int = 50
    ) -> List[Document]:
        splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(documents)
