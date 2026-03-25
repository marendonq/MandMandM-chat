param(
  [int]$TimeoutSeconds = 60
)

. $PSScriptRoot\_common.ps1

docker compose up -d redis | Out-Null

Wait-ForPort -Hostname "127.0.0.1" -Port 6379 -TimeoutSeconds $TimeoutSeconds

Set-EnvFromEnvExample

Run-Pytest -PytestArgs @("tests/test_redis_presence.py", "-q", "--tb=short")

