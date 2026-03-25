from copy import copy
from app.domain.entities.conversation import ConversationEntity, ConversationType
from app.domain.repositories.conversation import ConversationRepository


class ConversationInMemoryRepository(ConversationRepository):
    def __init__(self):
        self._store: list[dict] = []

    def add(self, conversation: ConversationEntity) -> ConversationEntity:
        self._store.append(copy(self._entity_to_row(conversation)))
        return conversation

    def get_by_id(self, conversation_id: str) -> ConversationEntity | None:
        for row in self._store:
            if row['id'] == conversation_id:
                return self._row_to_entity(row)
        return None

    def list_all(self) -> list[ConversationEntity]:
        return [self._row_to_entity(row) for row in self._store]

    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        for index, row in enumerate(self._store):
            if row['id'] == conversation.id:
                self._store[index] = copy(self._entity_to_row(conversation))
                return conversation
        self._store.append(copy(self._entity_to_row(conversation)))
        return conversation

    def delete(self, conversation_id: str) -> None:
        self._store = [row for row in self._store if row['id'] != conversation_id]

    @staticmethod
    def _entity_to_row(conversation: ConversationEntity) -> dict:
        return {
            'id': conversation.id,
            'type': conversation.type.value,
            'name': conversation.name,
            'description': conversation.description,
            'created_by': conversation.created_by,
            'created_at': conversation.created_at,
            'members': list(conversation.members),
            'admins': list(conversation.admins) if conversation.admins else None,
            'invitation_link': conversation.invitation_link,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> ConversationEntity:
        return ConversationEntity(
            id=row['id'],
            type=ConversationType(row['type']),
            name=row['name'],
            description=row.get('description'),
            created_by=row['created_by'],
            created_at=row['created_at'],
            members=list(row['members']),
            admins=list(row['admins']) if row.get('admins') else None,
            invitation_link=row.get('invitation_link'),
        )