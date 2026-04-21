# Microservicio: Message Service
# Puerto: 8004
# Maneja: /messages/*
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.container import Container
from app.infrastructure.handlers import messages
from fastapi.responses import HTMLResponse


load_dotenv(Path(__file__).parent.parent / '.env')


@app.get('/health', response_class=HTMLResponse)
async def health():
    return '<html><body>OK</body></html>'


app = FastAPI(title='Message Service', version='1.0')
container = Container()
app.container = container
app.include_router(messages.router)
container.wire(modules=['app.infrastructure.handlers.messages'])

