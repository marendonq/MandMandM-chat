from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import conversations

load_dotenv(Path(__file__).parent.parent / '.env')
configure_database_from_env()

app = FastAPI(title='Groups Service', version='1.0')
container = Container()
app.container = container
app.include_router(conversations.router)
container.wire(modules=['app.infrastructure.handlers.conversations'])

@app.get('/health')
async def health():
    return {'status': 'ok'}