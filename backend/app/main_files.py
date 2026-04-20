# Microservicio: File Service
# Puerto: 8005
# Maneja: /files/* y /file-metadata/*
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import file, files


load_dotenv(Path(__file__).parent.parent / '.env')
configure_database_from_env() # PostgreSQL para file_assets


app = FastAPI(title='File Service', version='1.0')
container = Container()
app.container = container
app.include_router(file.router)
app.include_router(files.router)
container.wire(modules=[
    'app.infrastructure.handlers.file',
    'app.infrastructure.handlers.files',
])

@app.get('/health')
async def health():
    return {'status': 'ok'}