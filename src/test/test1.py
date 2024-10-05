from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar

T = TypeVar("T")


class FooGenericAbstract(ABC, Generic[T]):

    @abstractmethod
    def func(self) -> T:
        pass


class Foo(FooGenericAbstract[Dict[str, int]]):

    def func(self) -> Dict[str, str]:
        pass
