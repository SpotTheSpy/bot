from abc import ABC, abstractmethod


class AbstractScene(ABC):
    @abstractmethod
    def on_back(
            self,
            *args,
            **kwargs
    ) -> None:
        pass
