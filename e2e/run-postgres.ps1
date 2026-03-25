param(
  [int]$TimeoutSeconds = 60
)

. $PSScriptRoot\_common.ps1

docker compose up -d postgres | Out-Null

Wait-ForPort -Hostname "127.0.0.1" -Port 5432 -TimeoutSeconds $TimeoutSeconds

Set-EnvFromEnvExample

Ensure-PostgresSchema

Run-Pytest -PytestArgs @("tests/test_postgres_integration.py", "-q", "--tb=short")

