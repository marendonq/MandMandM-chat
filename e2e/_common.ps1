param(
  [string]$EnvExampleRelativePath = "backend\.env.example"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"

function Set-EnvFromEnvExample {
  $envExamplePath = Join-Path $RepoRoot $EnvExampleRelativePath
  if (!(Test-Path $envExamplePath)) {
    throw "No existe $envExamplePath"
  }

  $lines = Get-Content $envExamplePath
  foreach ($line in $lines) {
    if ($line -match '^\s*DATABASE_URL=(.*)$') { $env:DATABASE_URL = $matches[1].Trim(); continue }
    if ($line -match '^\s*MONGO_URI=(.*)$') { $env:MONGO_URI = $matches[1].Trim(); continue }
    if ($line -match '^\s*REDIS_URI=(.*)$') { $env:REDIS_URI = $matches[1].Trim(); continue }
    if ($line -match '^\s*PRESENCE_REDIS_NAMESPACE=(.*)$') { $env:PRESENCE_REDIS_NAMESPACE = $matches[1].Trim(); continue }
    if ($line -match '^\s*PRESENCE_USER_TTL_SECONDS=(.*)$') { $env:PRESENCE_USER_TTL_SECONDS = $matches[1].Trim(); continue }
    if ($line -match '^\s*PRESENCE_RECEIPT_TTL_SECONDS=(.*)$') { $env:PRESENCE_RECEIPT_TTL_SECONDS = $matches[1].Trim(); continue }
  }
}

function Wait-ForPort {
  param(
    [Parameter(Mandatory=$true)][string]$Hostname,
    [Parameter(Mandatory=$true)][int]$Port,
    [int]$TimeoutSeconds = 60
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    $ok = Test-NetConnection -ComputerName $Hostname -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($ok) { return }
    Start-Sleep -Seconds 1
  }
  throw "Timeout esperando puerto $Hostname`:$Port en $TimeoutSeconds segundos"
}

function Ensure-PostgresSchema {
  # Crea tablas vía SQLAlchemy (idempotente) antes de ejecutar tests que validan existencia.
  Set-Location $BackendDir
  & python -c "from app.infrastructure.database.session import configure_database_from_env; configure_database_from_env(); print('postgres schema ensured')" | Out-Host
}

function Run-Pytest {
  param(
    [Parameter(Mandatory=$true)][string[]]$PytestArgs
  )

  Set-Location $BackendDir
  $env:PYTHONPATH = "."
  & pytest @PytestArgs
}

