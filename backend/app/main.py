"from pydantic import BaseModel
from datetime import datetime

from app.infrastructure.fast_api import create_app

# App monolítica: auth + OAuth + UI (create_app) + notificaciones (aquí)
app = create_app()


class CreateNotification(BaseModel):
    user_id: str
    type: str
    content: str
    status: str
    created_at: datetime


@app.get('/notifications/{user_id}')
async def get_user_notifications(user_id: str):
    return {'user_id': user_id, 'notifications': []}


@app.patch('/notifications/{item_id}/read')
async def mark_as_read(item_id: str, read: bool = True):
    status = 'read' if read else 'not_read'
    return {'item_id': item_id, 'status': status}


@app.post('/notifications/')
async def create_notification(notification: CreateNotification):
    return {'message': 'Notification created', 'data': notification.dict()}
"
