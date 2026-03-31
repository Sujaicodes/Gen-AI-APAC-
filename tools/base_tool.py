from abc import ABC, abstractmethod
from typing import Any, List

class BaseTool(ABC):
    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Any:
        pass