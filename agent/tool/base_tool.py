from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str

    def __init__(self, name: str = ""):
        self.name = name

    @abstractmethod
    def description(self) -> str:
        pass

    def example(self) -> [str]:
        return None

    def param(self):
        return {}

    @abstractmethod
    def action(self, llm, query, history, param: dict):
        pass


