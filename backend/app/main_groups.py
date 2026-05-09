"""Groups Service - FastAPI application entry point.

This module creates and configures the FastAPI application for the
groups/conversations microservice. It handles group and conversation
management including creation, member management, and admin operations.

Environment variables are loaded from .env file and the database
is configured from environment settings.
"""

# Microservicio: Groups Service
# Puerto: 8007
# Maneja: /conversations/* (gestión de grupos y conversaciones privadas)
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import conversations

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')
# Configure database connection
configure_database_from_env()

# Create FastAPI application instance
app = FastAPI(title='Groups Service', version='1.0')
# Initialize dependency injection container
container = Container()
app.container = container

# Register conversation router (handles groups and conversations)
app.include_router(conversations.router)
# Wire container to handler modules for dependency injection
container.wire(modules=['app.infrastructure.handlers.conversations'])



@app.get('/health')
async def health():
    """Health check endpoint for the groups service.

    Returns:
        dict: Status and service name.
    """
    return {'status': 'ok', 'service': 'groups'}
