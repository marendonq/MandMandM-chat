from abc import ABC, abstractmethod
from app.domain.entities.group import GroupEntity


class GroupUseCases(ABC):
    @abstractmethod
    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def list_groups(self) -> list[GroupEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_group(self, group_id: str) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def add_user_to_group(self, group_id: str, actor_id: str, user_id: str) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def delete_user_from_group(self, group_id: str, actor_id: str, user_id: str) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def update_admin(self, group_id: str, actor_id: str, user_id: str) -> GroupEntity:
        raise NotImplementedError

    @abstractmethod
    def exit_group(self, group_id: str, user_id: str) -> GroupEntity:
        raise NotImplementedError
