from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.product import ProductEntity


class ProductRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> ProductEntity:
        raise NotImplementedError

    @abstractmethod
    def add(self, product: ProductEntity) -> ProductEntity:
        raise NotImplementedError

    @abstractmethod
    def update(self, product: ProductEntity) -> ProductEntity:
        raise NotImplementedError
