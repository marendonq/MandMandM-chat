from pydantic import BaseModel


class FileImage(BaseModel):
    id: int
    uploaded_by: str
    file_name: str
    size: int
    content_type: str
    category: str
    created_at: str