from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.container import Container
from app.infrastructure.handlers import presence

load_dotenv(Path(__file__).parent.parent / '.env')

app = FastAPI(title='Presence Service', version='1.0')
container = Container()
app.container = container
app.include_router(presence.router)
container.wire(modules=['app.infrastructure.handlers.presence'])

@app.get('/health')
async def health():
    return {'status': 'ok'}