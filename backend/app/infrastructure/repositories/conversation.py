"""Conversation repository implementations for in-memory and MongoDB.

This module provides two implementations of the ConversationRepository:
- ConversationInMemoryRepository: For testing and development
- MongoConversationRepository: For production use with MongoDB
"""

from copy import copy

from pymongo.database import Database

from app.domain.entities.conversation import ConversationEntity, ConversationType
from app.domain.repositories.conversation import ConversationRepository


class ConversationInMemoryRepository(ConversationRepository):
    """In-memory repository for ConversationEntity.

    Stores conversation data in a list of dictionaries. Useful for testing
    and development without requiring a database connection.
    """

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: list[dict] = []

    def add(self, conversation: ConversationEntity) -> ConversationEntity:
        """Persist a new conversation.

        Args:
            conversation: The ConversationEntity to persist.

        Returns:
            The persisted ConversationEntity.
        """
        self._store.append(copy(self._entity_to_row(conversation)))
        return conversation

    def get_by_id(self, conversation_id: str) -> ConversationEntity | None:
        """Retrieve a conversation by its ID.

        Args:
            conversation_id: The unique conversation identifier.

        Returns:
            The ConversationEntity if found, otherwise None.
        """
        for row in self._store:
            if row['id'] == conversation_id:
                return self._row_to_entity(row)
        return None

    def list_all(self) -> list[ConversationEntity]:
        """List all conversations.

        Returns:
            A list of all ConversationEntity objects.
        """
        return [self._row_to_entity(row) for row in self._store]

    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        """Update an existing conversation.

        Args:
            conversation: The ConversationEntity with updated data.

        Returns:
            The updated ConversationEntity.
        """
        for index, row in enumerate(self._store):
            if row['id'] == conversation.id:
                self._store[index] = copy(self._entity_to_row(conversation))
                return conversation
        self._store.append(copy(self._entity_to_row(conversation)))
        return conversation

    def delete(self, conversation_id: str) -> None:
        """Delete a conversation by its ID.

        Args:
            conversation_id: The unique conversation identifier to delete.
        """
        self._store = [row for row in self._store if row['id'] != conversation_id]

    @staticmethod
    def _entity_to_row(conversation: ConversationEntity) -> dict:
        """Convert a ConversationEntity to a dictionary for storage.

        Args:
            conversation: The ConversationEntity to convert.

        Returns:
            A dictionary representation of the conversation.
        """
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
        """Convert a storage dictionary row to a ConversationEntity.

        Args:
            row: Dictionary containing conversation data.

        Returns:
            A ConversationEntity constructed from the row data.
        """
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


class MongoConversationRepository(ConversationRepository):
    """MongoDB repository for ConversationEntity.

    Stores conversation data in a MongoDB collection. Suitable for
    production use with persistent storage.
    """

    def __init__(self, database: Database):
        """Initialize the MongoDB repository.

        Args:
            database: The MongoDB database instance to use.
        """
        self._collection = database["conversations"]

    @staticmethod
    def _entity_to_row(conversation: ConversationEntity) -> dict:
        """Convert a ConversationEntity to a MongoDB document.

        Args:
            conversation: The ConversationEntity to convert.

        Returns:
            A dictionary suitable for MongoDB storage.
        """
        return ConversationInMemoryRepository._entity_to_row(conversation)

    @staticmethod
    def _row_to_entity(row: dict) -> ConversationEntity:
        """Convert a MongoDB document to a ConversationEntity.

        Args:
            row: MongoDB document containing conversation data.

        Returns:
            A ConversationEntity constructed from the document.
        """
        return ConversationInMemoryRepository._row_to_entity(row)

    def add(self, conversation: ConversationEntity) -> ConversationEntity:
        """Persist a new conversation to MongoDB.

        Args:
            conversation: The ConversationEntity to persist.

        Returns:
            The persisted ConversationEntity.
        """
        self._collection.insert_one(self._entity_to_row(conversation))
        return conversation

    def get_by_id(self, conversation_id: str) -> ConversationEntity | None:
        """Retrieve a conversation by its ID from MongoDB.

        Args:
            conversation_id: The unique conversation identifier.

        Returns:
            The ConversationEntity if found, otherwise None.
        """
        row = self._collection.find_one({"id": conversation_id}, {"_id": 0})
        return self._row_to_entity(row) if row else None

    def list_all(self) -> list[ConversationEntity]:
        """List all conversations from MongoDB.

        Returns:
            A list of all ConversationEntity objects.
        """
        return [self._row_to_entity(row) for row in self._collection.find({}, {"_id": 0})]

    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        """Update an existing conversation in MongoDB.

        Uses upsert to insert if the conversation doesn't exist.

        Args:
            conversation: The ConversationEntity with updated data.

        Returns:
            The updated ConversationEntity.
        """
        self._collection.replace_one(
            {"id": conversation.id},
            self._entity_to_row(conversation),
            upsert=True,
        )
        return conversation

    def delete(self, conversation_id: str) -> None:
        """Delete a conversation from MongoDB by its ID.

        Args:
            conversation_id: The unique conversation identifier to delete.
        """
        self._collection.delete_one({"id": conversation_id})