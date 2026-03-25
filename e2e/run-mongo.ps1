param(
  [int]$TimeoutSeconds = 60
)

. $PSScriptRoot\_common.ps1

docker compose up -d mongo | Out-Null

Wait-ForPort -Hostname "127.0.0.1" -Port 27017 -TimeoutSeconds $TimeoutSeconds

Set-EnvFromEnvExample

Run-Pytest -PytestArgs @("tests/test_mongo_messages.py", "-q", "--tb=short")

