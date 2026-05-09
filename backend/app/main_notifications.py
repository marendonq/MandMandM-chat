"""Notification Service - FastAPI application entry point.

This module creates and configures the FastAPI application for the
notification microservice. It handles notification creation,
retrieval, and status management (marking as read/delivered).

Environment variables are loaded from .env file and the database
is configured from environment settings.
"""

from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import notifications

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')
# Configure database connection
configure_database_from_env()

# Create FastAPI application instance
app = FastAPI(title='Notification Service', version='1.0')
# Initialize dependency injection container
container = Container()
app.container = container

# Register notification router
app.include_router(notifications.router)
# Wire container to handler modules for dependency injection
container.wire(modules=['app.infrastructure.handlers.notifications'])


@app.get('/health')
async def health():
    """Health check endpoint for the notification service.

    Returns:
        dict: Status and service name.
    """
    return {'status': 'ok', 'service': 'notifications'}