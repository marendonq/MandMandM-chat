<#
.SYNOPSIS
  Smoke-test de todos los microservicios a través del gateway (Ingress o local).

.DESCRIPTION
  Verifica que cada microservicio responde correctamente simulando un flujo
  real de usuario: registro → perfil → contacto → grupo/conversación → mensaje
  → presencia → notificación → limpieza.

  Funciona tanto en local (monolito en :8000) como en producción (Ingress EC2).

.PARAMETER BaseUrl
  URL base del gateway. Ejemplos:
    Local (monolito)  : http://127.0.0.1:8000     (default)
    Producción (EC2)  : http://3.210.139.202:31442

.PARAMETER StopOnError
  Si se pasa, el script falla en el primer endpoint que devuelva error.

.EXAMPLE
  # Local
  .\smoke_test_microservices.ps1

  # Producción
  .\smoke_test_microservices.ps1 -BaseUrl "http://3.210.139.202:31442"

  # Fallo rápido
  .\smoke_test_microservices.ps1 -StopOnError
#>

param(
  [string]$BaseUrl     = "http://127.0.0.1:8000",
  [switch]$StopOnError
)

# ─── Paleta de colores ────────────────────────────────────────────────────────
function Write-Ok   ($msg) { Write-Host "  ✅ $msg" -ForegroundColor Green }
function Write-Fail ($msg) { Write-Host "  ❌ $msg" -ForegroundColor Red }
function Write-Info ($msg) { Write-Host "  ℹ  $msg" -ForegroundColor Cyan }
function Write-Step ($msg) { Write-Host "`n▶ $msg" -ForegroundColor Yellow }

$global:passed = 0
$global:failed = 0

# ─── Helpers ─────────────────────────────────────────────────────────────────
function Invoke-Api {
  param(
    [string]$Method,
    [string]$Path,
    [object]$Body     = $null,
    [int]   $Expected = 200
  )

  $url     = $BaseUrl.TrimEnd('/') + $Path
  $headers = @{ "Content-Type" = "application/json" }

  try {
    $params = @{
      Method             = $Method
      Uri                = $url
      Headers            = $headers
      TimeoutSec         = 20
      ErrorAction        = "Stop"
    }
    if ($null -ne $Body) {
      $params["Body"] = ($Body | ConvertTo-Json -Depth 10 -Compress)
    }

    $response = Invoke-RestMethod @params
    $global:passed++
    return $response
  }
  catch [System.Net.WebException] {
    $sc = [int]$_.Exception.Response.StatusCode
    # Códigos esperados distintos de 200 (ej. 204 No Content)
    if ($sc -eq $Expected) {
      $global:passed++
      return $null
    }
    $global:failed++
    Write-Fail "HTTP $sc → $Method $Path"
    if ($StopOnError) { throw }
    return $null
  }
  catch {
    $global:failed++
    Write-Fail "Excepción → $Method $Path : $_"
    if ($StopOnError) { throw }
    return $null
  }
}

function Assert-Field {
  param($Obj, [string]$Field, [string]$Context)
  if ($null -eq $Obj -or -not $Obj.PSObject.Properties[$Field]) {
    $global:failed++
    Write-Fail "[$Context] Campo '$Field' no presente en la respuesta"
    return $false
  }
  return $true
}

# ─── Banner ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║       MandMandM — Smoke Test de Microservicios               ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host "  Gateway : $BaseUrl" -ForegroundColor White
Write-Host "  Hora    : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White

$suffix = [guid]::NewGuid().ToString().Substring(0, 8)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. HEALTH CHECKS — cada microservicio expone /health
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "1. Health checks de microservicios"

# En despliegue cada servicio tiene su propio /health pero todos pasan por Ingress.
# En local (monolito) sólo hay un /health en :8000.
# Probamos el /health del gateway (auth service es el que responde en / de la app monolito).
$h = Invoke-Api -Method GET -Path "/health"
if ($null -ne $h) {
  Write-Ok "GET /health → OK (servicio principal respondió)"
} else {
  Write-Fail "GET /health → sin respuesta"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. AUTH — POST /auth/register + POST /auth/login
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "2. Auth Service → /auth/*"

$emailA    = "smoke_a_${suffix}@example.com"
$passwordA = "Password123!"

Write-Info "POST /auth/register (usuario A)"
$regA = Invoke-Api -Method POST -Path "/auth/register" -Body @{
  email     = $emailA
  password  = $passwordA
  full_name = "Smoke User A"
  phone     = "57" + ((Get-Random -Minimum 1000000000 -Maximum 9999999999).ToString())
}
if ($null -ne $regA -and (Assert-Field $regA "access_token" "register")) {
  Write-Ok "Registro OK → user.id=$($regA.user.id)"
  $userIdA    = $regA.user.id
  $tokenA     = $regA.access_token
  $uniqueIdA  = $regA.unique_id
} else {
  Write-Fail "No se pudo registrar usuario A — abortando pasos dependientes"
  $userIdA   = $null
  $tokenA    = $null
  $uniqueIdA = $null
}

Write-Info "POST /auth/login"
$login = Invoke-Api -Method POST -Path "/auth/login" -Body @{
  email    = $emailA
  password = $passwordA
}
if ($null -ne $login -and (Assert-Field $login "access_token" "login")) {
  Write-Ok "Login OK → token recibido"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. USERS — oauth-sync + GET perfil + contactos
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "3. Users Service → /users/*"

Write-Info "POST /users/oauth-sync (usuario B)"
$syncB = Invoke-Api -Method POST -Path "/users/oauth-sync" -Body @{
  provider  = "google"
  subject   = "smoke-b-$suffix"
  email     = "smoke_b_${suffix}@example.com"
  full_name = "Smoke User B"
}
if ($null -ne $syncB -and (Assert-Field $syncB "id" "oauth-sync")) {
  Write-Ok "oauth-sync B OK → id=$($syncB.id) unique_id=$($syncB.unique_id)"
  $userIdB   = $syncB.id
  $uniqueIdB = $syncB.unique_id
} else {
  Write-Fail "No se pudo sincronizar usuario B"
  $userIdB   = $null
  $uniqueIdB = $null
}

if ($null -ne $userIdA) {
  Write-Info "GET /users/$userIdA"
  $prof = Invoke-Api -Method GET -Path "/users/$userIdA"
  if ($null -ne $prof -and (Assert-Field $prof "id" "GET /users")) {
    Write-Ok "Perfil OK → email=$($prof.email)"
  }
}

if ($null -ne $userIdA -and $null -ne $uniqueIdB) {
  Write-Info "POST /users/$userIdA/contacts (A agrega a B)"
  $contact = Invoke-Api -Method POST -Path "/users/$userIdA/contacts" -Body @{
    target_unique_id = $uniqueIdB
  }
  if ($null -ne $contact) {
    Write-Ok "Contacto A→B creado OK"
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. GROUPS (conversations) — CRUD de conversaciones
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "4. Groups Service → /conversations/*"

$convId = $null

if ($null -ne $userIdA -and $null -ne $userIdB) {
  Write-Info "POST /conversations/ (crear grupo)"
  $grp = Invoke-Api -Method POST -Path "/conversations/" -Body @{
    type        = "group"
    name        = "smoke-group-$suffix"
    description = "Smoke test $suffix"
    created_by  = $userIdA
    members     = @($userIdB)
  }
  if ($null -ne $grp -and (Assert-Field $grp "id" "POST /conversations")) {
    Write-Ok "Grupo creado OK → id=$($grp.id)"
    $convId = $grp.id
    $members = $grp.members
    if ($members -contains $userIdA -and $members -contains $userIdB) {
      Write-Ok "Ambos miembros presentes en el grupo ✓"
    } else {
      Write-Fail "Miembros incorrectos: $($members -join ', ')"
    }
  }

  Write-Info "GET /conversations/ (listar)"
  $list = Invoke-Api -Method GET -Path "/conversations/"
  if ($null -ne $list) {
    Write-Ok "Listado OK → $($list.Count) conversación(es)"
  }

  if ($null -ne $convId) {
    Write-Info "GET /conversations/$convId"
    $single = Invoke-Api -Method GET -Path "/conversations/$convId"
    if ($null -ne $single -and $single.id -eq $convId) {
      Write-Ok "GET individual OK → type=$($single.type)"
    }

    Write-Info "POST /conversations/private (chat 1:1)"
    $priv = Invoke-Api -Method POST -Path "/conversations/private" -Body @{
      created_by    = $userIdA
      participant_two = $userIdB
    }
    if ($null -ne $priv -and (Assert-Field $priv "id" "POST /conversations/private")) {
      Write-Ok "Chat privado OK → id=$($priv.id)"
    }

    Write-Info "GET /conversations/$convId/messages (mensajes paginados)"
    $msgs = Invoke-Api -Method GET -Path "/conversations/$convId/messages?limit=10"
    if ($null -ne $msgs) {
      Write-Ok "Mensajes OK → $($msgs.total) mensaje(s)"
    }
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 5. MESSAGES — enviar un mensaje
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "5. Messages Service → /messages/*"

$messageId = $null

if ($null -ne $convId -and $null -ne $userIdA -and $null -ne $userIdB) {
  Write-Info "POST /messages/ (enviar mensaje)"
  $msg = Invoke-Api -Method POST -Path "/messages/" -Body @{
    conversation_id = $convId
    sender_id       = $userIdA
    recipient_id    = $userIdB
    content         = "Hola desde smoke test $suffix"
  }
  if ($null -ne $msg) {
    $messageId = if ($msg.message_id) { $msg.message_id } elseif ($msg.id) { $msg.id } else { $null }
    Write-Ok "Mensaje enviado OK → id=$messageId"
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 6. PRESENCE — heartbeat + recibos de mensaje
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "6. Presence Service → /presence/*"

if ($null -ne $userIdA) {
  Write-Info "POST /presence/heartbeat"
  Invoke-Api -Method POST -Path "/presence/heartbeat" -Body @{ user_id = $userIdA } | Out-Null
  Write-Ok "Heartbeat enviado"

  Write-Info "GET /presence/users/$userIdA"
  $pres = Invoke-Api -Method GET -Path "/presence/users/$userIdA"
  if ($null -ne $pres -and (Assert-Field $pres "activity_status" "presence")) {
    Write-Ok "Presencia OK → status=$($pres.activity_status)"
  }
}

$receiptMsgId = [guid]::NewGuid().ToString()
if ($null -ne $userIdA -and $null -ne $userIdB) {
  Write-Info "POST /presence/messages (registro SENT)"
  Invoke-Api -Method POST -Path "/presence/messages" -Body @{
    message_id   = $receiptMsgId
    sender_id    = $userIdA
    recipient_id = $userIdB
  } | Out-Null

  Write-Info "POST /presence/messages/$receiptMsgId/delivered"
  Invoke-Api -Method POST -Path "/presence/messages/$receiptMsgId/delivered" -Body @{
    recipient_id = $userIdB
  } | Out-Null

  Write-Info "POST /presence/messages/$receiptMsgId/read"
  Invoke-Api -Method POST -Path "/presence/messages/$receiptMsgId/read" -Body @{
    recipient_id = $userIdB
  } | Out-Null

  Write-Info "GET /presence/messages/$receiptMsgId"
  $receipts = Invoke-Api -Method GET -Path "/presence/messages/$receiptMsgId"
  if ($null -ne $receipts) {
    $receiptList = @($receipts.receipts)
    $readReceipt = $receiptList | Where-Object { $_ -and $_.status -eq "READ" }
    if ($null -ne $readReceipt -and $readReceipt.Count -gt 0) {
      Write-Ok "Recibo READ confirmado ✓"
    } else {
      Write-Fail "Recibo no está en estado READ. Respuesta: $($receipts | ConvertTo-Json -Compress)"
    }
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 7. NOTIFICATIONS — crear y listar
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "7. Notifications Service → /notifications/*"

if ($null -ne $userIdA) {
  Write-Info "POST /notifications/"
  $notif = Invoke-Api -Method POST -Path "/notifications/" -Body @{
    user_id = $userIdA
    type    = "SMOKE_TEST"
    content = "notificacion smoke $suffix"
  }
  if ($null -ne $notif -and (Assert-Field $notif "id" "POST /notifications")) {
    Write-Ok "Notificación creada OK → id=$($notif.id)"
  }

  Write-Info "GET /notifications/$userIdA"
  $notifList = Invoke-Api -Method GET -Path "/notifications/$userIdA"
  if ($null -ne $notifList) {
    Write-Ok "Listado notificaciones OK → $($notifList.Count) notificación(es)"
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 8. FILES — file-metadata (sin subir binario)
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "8. Files Service → /file-metadata/*"

if ($null -ne $userIdA) {
  Write-Info "POST /file-metadata/"
  $fmeta = Invoke-Api -Method POST -Path "/file-metadata/" -Body @{
    owner_profile_id = $userIdA
    original_name    = "smoke-${suffix}.txt"
    mime_type        = "text/plain"
    size_bytes       = 42
    storage_key      = "local/smoke-${suffix}/file.txt"
  }
  if ($null -ne $fmeta -and (Assert-Field $fmeta "id" "POST /file-metadata")) {
    Write-Ok "File-metadata creado OK → id=$($fmeta.id)"

    Write-Info "GET /file-metadata/by-owner/$userIdA"
    $flist = Invoke-Api -Method GET -Path "/file-metadata/by-owner/$userIdA"
    if ($null -ne $flist) {
      Write-Ok "Listado file-metadata OK → $($flist.items.Count) archivo(s)"
    }
  }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 9. LIMPIEZA
# ═══════════════════════════════════════════════════════════════════════════════
Write-Step "9. Limpieza"

if ($null -ne $convId -and $null -ne $userIdA) {
  Write-Info "DELETE /conversations/$convId"
  Invoke-Api -Method DELETE -Path "/conversations/$convId" -Body @{ actor_id = $userIdA } | Out-Null
  Write-Ok "Conversación eliminada"
}

if ($null -ne $userIdA) {
  Write-Info "DELETE /users/$userIdA/contacts/$userIdB"
  Invoke-Api -Method DELETE -Path "/users/$userIdA/contacts/$userIdB" | Out-Null

  Write-Info "DELETE /users/$userIdA"
  Invoke-Api -Method DELETE -Path "/users/$userIdA" | Out-Null
  Write-Ok "Usuario A eliminado"
}

if ($null -ne $userIdB) {
  Write-Info "DELETE /users/$userIdB"
  Invoke-Api -Method DELETE -Path "/users/$userIdB" | Out-Null
  Write-Ok "Usuario B eliminado"
}

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════════
$total = $global:passed + $global:failed

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  RESUMEN SMOKE TEST" -ForegroundColor White
Write-Host "  Gateway   : $BaseUrl" -ForegroundColor White
Write-Host "  Total     : $total checks" -ForegroundColor White
Write-Host "  Pasaron   : $($global:passed)" -ForegroundColor Green
Write-Host "  Fallaron  : $($global:failed)" -ForegroundColor $(if ($global:failed -gt 0) { "Red" } else { "Green" })
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Magenta

if ($global:failed -gt 0) {
  Write-Host ""
  Write-Host "  ⚠  Algunos endpoints fallaron. Revisa los ❌ arriba." -ForegroundColor Red
  exit 1
} else {
  Write-Host ""
  Write-Host "  🎉 Todos los checks pasaron correctamente." -ForegroundColor Green
  exit 0
}
