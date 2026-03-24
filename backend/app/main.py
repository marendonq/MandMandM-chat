from app.infrastructure.fast_api import create_app

# App monolítica: compone los micro-modulos (Auth/Groups/Notifications) con DI.
app = create_app()

