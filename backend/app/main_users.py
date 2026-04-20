# Microservicio: User & Presence Service
# Puerto: 8002
# Maneja: /users/* y /presence/*
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import users, presence


load_dotenv(Path(__file__).parent.parent / '.env')
configure_database_from_env() # PostgreSQL + Redis


app = FastAPI(title='User Service', version='1.0')
container = Container()
app.container = container
app.include_router(users.router)
app.include_router(presence.router)
container.wire(modules=[
    'app.infrastructure.handlers.users',
    'app.infrastructure.handlers.presence',
])

@app.get('/health')
async def health():
    return {'status': 'ok'}