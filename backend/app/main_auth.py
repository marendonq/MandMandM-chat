from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import auth, oauth_redirect


load_dotenv(Path(__file__).parent.parent / '.env')
configure_database_from_env() # Solo necesita PostgreSQL (usuarios)


app = FastAPI(title='Auth Service', version='1.0')
container = Container()
app.container = container

# Solo registra los routers de autenticación
app.include_router(auth.router)
app.include_router(oauth_redirect.router)
container.wire(modules=[
    'app.infrastructure.handlers.auth',
    'app.infrastructure.handlers.oauth_redirect',
])

@app.get('/health')
async def health():
    return {'status': 'ok'}