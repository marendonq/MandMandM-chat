param(
  [int]$TimeoutSeconds = 90
)

. $PSScriptRoot\_common.ps1

# Levanta las 3 bases en Docker
docker compose up -d postgres mongo redis | Out-Null

Wait-ForPort -Hostname "127.0.0.1" -Port 5432 -TimeoutSeconds $TimeoutSeconds
Wait-ForPort -Hostname "127.0.0.1" -Port 27017 -TimeoutSeconds $TimeoutSeconds
Wait-ForPort -Hostname "127.0.0.1" -Port 6379 -TimeoutSeconds $TimeoutSeconds

Set-EnvFromEnvExample

# Ejecuta toda la suite e2e (valida Postgres, Mongo y Redis)
Ensure-PostgresSchema

Run-Pytest -PytestArgs @("tests/", "-q", "--tb=short")

