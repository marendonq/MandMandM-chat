import os
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DB_NAME = "groupsapp_messages"


class MongoConnection:
    def __init__(self, uri: str | None = None, db_name: str | None = None):
        self.uri = uri or os.getenv("MONGO_URI", DEFAULT_MONGO_URI)
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", DEFAULT_MONGO_DB_NAME)
        self.client = MongoClient(self.uri)
        self.database = self.client[self.db_name]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.database["conversations"].create_index([("members", ASCENDING)], name="members_idx")
        self.database["conversations"].create_index([("type", ASCENDING)], name="type_idx")
        self.database["messages"].create_index(
            [("conversation_id", ASCENDING), ("created_at", ASCENDING)],
            name="conversation_created_at_idx",
        )
        self.database["messages"].create_index([("sender_id", ASCENDING)], name="sender_id_idx")

    def get_database(self) -> Database:
        return self.database

    def close(self) -> None:
        self.client.close()
