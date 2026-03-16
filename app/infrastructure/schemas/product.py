from pydantic import BaseModel


class create_notification(BaseModel):   # creacion de la notificacion, se le pasan los datos que se necesitan para crearla
    Header: user_id: str
    Body text: str
    cta: str
