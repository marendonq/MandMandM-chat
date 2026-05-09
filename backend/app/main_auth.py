"""Auth Service - FastAPI application entry point.

This module creates and configures the FastAPI application for the
authentication microservice. It handles user registration, login,
and OAuth redirect flows.

Environment variables are loaded from .env file and the database
is configured from environment settings (PostgreSQL for users).
"""

from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import auth, oauth_redirect
from fastapi.responses import HTMLResponse


# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')
# Configure database connection (PostgreSQL for user data)
configure_database_from_env()


# Create FastAPI application instance
app = FastAPI(title='Auth Service', version='1.0')
# Initialize dependency injection container
container = Container()
app.container = container


# Register authentication routers
app.include_router(auth.router)
app.include_router(oauth_redirect.router)
# Wire container to handler modules for dependency injection
container.wire(modules=[
    'app.infrastructure.handlers.auth',
    'app.infrastructure.handlers.oauth_redirect',
])


@app.get('/health', response_class=HTMLResponse)
async def health():
    """Health check endpoint for the auth service.

    Returns:
        HTMLResponse: Simple HTML page with 'OK' status.
    """
    return '<html><body>OK</body></html>'

