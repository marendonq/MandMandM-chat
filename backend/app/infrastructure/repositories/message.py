from __future__ import annotations

from datetime import datetime
from typing import Optional

from pymongo.database import Database

from app.domain.entities.message import MessageEntity, MessageType
from app.domain.repositories.message import MessageRepository


class MongoMessageRepository(MessageRepository):
    def __init__(self, database: Database):
        self._collection = database["messages"]

    def save(self, message: MessageEntity) -> MessageEntity:
        self._collection.insert_one(self._entity_to_document(message))
        return message

    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        document = self._collection.find_one({"id": message_id}, {"_id": 0})
        return self._document_to_entity(document) if document else None

    def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> list[MessageEntity]:
        query: dict = {"conversation_id": conversation_id}
        if before is not None:
            query["created_at"] = {"$lt": before}
        cursor = self._collection.find(query, {"_id": 0}).sort("created_at", 1).limit(limit)
        return [self._document_to_entity(document) for document in cursor]

    def delete(self, message_id: str) -> bool:
        result = self._collection.update_one(
            {"id": message_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    def hard_delete(self, message_id: str) -> bool:
        result = self._collection.delete_one({"id": message_id})
        return result.deleted_count > 0

    def update(self, message: MessageEntity) -> MessageEntity:
        self._collection.replace_one(
            {"id": message.id},
            self._entity_to_document(message),
            upsert=True,
        )
        return message

    @staticmethod
    def _entity_to_document(message: MessageEntity) -> dict:
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "message_type": message.message_type.value,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "is_deleted": message.is_deleted,
            "file_id": message.file_id,
        }

    @staticmethod
    def _document_to_entity(document: dict) -> MessageEntity:
        return MessageEntity(
            id=document["id"],
            conversation_id=document["conversation_id"],
            sender_id=document["sender_id"],
            content=document["content"],
            message_type=MessageType(document["message_type"]),
            created_at=document["created_at"],
            updated_at=document.get("updated_at"),
            is_deleted=document.get("is_deleted", False),
            file_id=document.get("file_id"),
        )
