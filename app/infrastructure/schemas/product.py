from pydantic import BaseModel


class ProductInput(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    image: str


class ProductOutput(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    image: str


class create_notification(BaseModel):
    """Creación de notificación (módulo notificaciones)."""
    user_id: str
    text: str
    cta: str
