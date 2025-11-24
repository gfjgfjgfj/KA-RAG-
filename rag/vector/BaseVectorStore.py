from abc import ABC, abstractmethod


class BaseVectorStore(ABC):

    @abstractmethod
    def insert(self, vectors: list[float], content: str, **param) -> bool:
        pass

    @abstractmethod
    def query(self, question_vectors: list[float], **param):
        pass




