from abc import ABC, abstractmethod
from app.domain.entities.group import GroupEntity


class GroupRepository(ABC):
    @abstractmethod
    def add(self, group: GroupEntity) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, group_id: str) -> GroupEntity | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[GroupEntity]:
        raise NotImplementedError

    @abstractmethod
    def update(self, group: GroupEntity) -> GroupEntity:
        raise NotImplementedError
