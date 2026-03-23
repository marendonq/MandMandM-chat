from copy import copy
from app.domain.entities.group import GroupEntity
from app.domain.repositories.group import GroupRepository


class GroupInMemoryRepository(GroupRepository):
    def __init__(self):
        self._store: list[dict] = []

    def add(self, group: GroupEntity) -> GroupEntity:
        self._store.append(copy(self._entity_to_row(group)))
        return group

    def get_by_id(self, group_id: str) -> GroupEntity | None:
        for row in self._store:
            if row["id"] == group_id:
                return self._row_to_entity(row)
        return None

    def list_all(self) -> list[GroupEntity]:
        return [self._row_to_entity(row) for row in self._store]

    def update(self, group: GroupEntity) -> GroupEntity:
        for index, row in enumerate(self._store):
            if row["id"] == group.id:
                self._store[index] = copy(self._entity_to_row(group))
                return group
        self._store.append(copy(self._entity_to_row(group)))
        return group

    @staticmethod
    def _entity_to_row(group: GroupEntity) -> dict:
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "created_at": group.created_at,
            "members": list(group.members),
            "admins": list(group.admins),
            "invitation_link": group.invitation_link,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> GroupEntity:
        return GroupEntity(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_by=row["created_by"],
            created_at=row["created_at"],
            members=list(row["members"]),
            admins=list(row["admins"]),
            invitation_link=row.get("invitation_link"),
        )
