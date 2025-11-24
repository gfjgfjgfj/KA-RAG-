from abc import ABC, abstractmethod


class BaseTemplate(ABC):

    @abstractmethod
    def handle(self, query: str, **param) -> str:
        pass


