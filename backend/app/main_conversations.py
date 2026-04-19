# Microservicio: Conversation Service
# Puerto: 8003
# Maneja: /conversations/*
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.container import Container
from app.infrastructure.handlers import conversations


load_dotenv(Path(__file__).parent.parent / '.env')


app = FastAPI(title='Conversation Service', version='1.0')
container = Container()
app.container = container
app.include_router(conversations.router)
container.wire(modules=['app.infrastructure.handlers.conversations'])