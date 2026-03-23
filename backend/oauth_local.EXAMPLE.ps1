# Copia este archivo como oauth_local.ps1 y rellena tus valores.
# oauth_local.ps1 está en .gitignore y NO se sube al repositorio.
#
# Uso (desde la carpeta backend):
#   . .\oauth_local.ps1
#   ..\venv\Scripts\uvicorn.exe app.main:app --reload

$env:OAUTH_GOOGLE_CLIENT_ID = "TU_CLIENT_ID.apps.googleusercontent.com"
$env:OAUTH_GOOGLE_CLIENT_SECRET = "GOCSPX-tu_secreto"
$env:OAUTH_PUBLIC_BASE_URL = "http://127.0.0.1:8000"

# Opcional: firma de JWT distinta en producción
# $env:JWT_SECRET = "una-cadena-larga-y-secreta"
