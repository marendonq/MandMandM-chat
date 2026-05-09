"""File Service - FastAPI application entry point.

This module creates and configures the FastAPI application for the
file microservice. It handles file uploads, downloads, metadata
management, and file asset registration.

Endpoints:
    /files/* - Binary file upload, download, and deletion.
    /file-metadata/* - File asset metadata registration and retrieval.

Port: 8005

Environment variables are loaded from .env file and the database
is configured from environment settings.
"""

from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.container import Container
from app.infrastructure.handlers import file, files


# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')
# Configure database connection
configure_database_from_env()


# Create FastAPI application instance
app = FastAPI(title='File Service', version='1.0')
# Initialize dependency injection container
container = Container()
app.container = container

# Register file handlers routers
app.include_router(file.router)      # /files/* - binary file operations
app.include_router(files.router)     # /file-metadata/* - metadata operations

# Wire container to handler modules for dependency injection
container.wire(modules=[
    'app.infrastructure.handlers.file',
    'app.infrastructure.handlers.files',
])


@app.get('/health')
async def health():
    """Health check endpoint for the file service.

    Returns:
        dict: Status and service name.
    """
    return {'status': 'ok', 'service': 'files'}