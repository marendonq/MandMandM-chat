param(
  [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

# Usuario A (derivado del access_token que pasaste; aquí usamos solo los campos necesarios)
$userA_id = "8ae67475-2b78-4916-a826-5ef3d713fa46"
$userA_email = "miguelangelrq2005@gmail.com"
$userA_full_name = "Miguel Angel Rendon Quintero"
$userA_unique_id = "usr-8ae67475"
$userA_oauth_provider = "google"
$userA_oauth_subject = $userA_id
$userA_picture = "https://lh3.googleusercontent.com/a/ACg8ocIHXuJ9OUxKspGIaL58maCNj3IebCVbXjYZPwACOTE9dy6aGpQbog=s96-c"

# Usuario B (se crea vía oauth-sync)
$provider = "google"
$subjectB = "sim-b-" + [guid]::NewGuid().ToString()
$emailB = "b_" + [guid]::NewGuid().ToString().Substring(0,8) + "@example.com"
$fullNameB = "User B"
$pictureB = $null

function Invoke-Api {
  param(
    [Parameter(Mandatory=$true)][string]$Method,
    [Parameter(Mandatory=$true)][string]$Path,
    [object]$Body = $null
  )

  $url = $BaseUrl.TrimEnd('/') + $Path
  $headers = @{ "Content-Type" = "application/json" }
  if ($Body -ne $null) {
    $json = ($Body | ConvertTo-Json -Depth 10 -Compress)
    return Invoke-RestMethod -Method $Method -Uri $url -Headers $headers -Body $json -TimeoutSec 30
  }
  return Invoke-RestMethod -Method $Method -Uri $url -Headers $headers -TimeoutSec 30
}

function Exec-PSQL {
  param(
    [Parameter(Mandatory=$true)][string]$Sql
  )
  docker exec mandmandm-pg psql -U mandmandm -d mandmandm -t -A -c $Sql
}

function Exec-Mongo {
  param(
    [Parameter(Mandatory=$true)][string]$Eval
  )
  docker exec mandmandm-mongo mongosh --quiet --eval $Eval
}

function Exec-Redis {
  param(
    [Parameter(Mandatory=$true)][string[]]$CmdParts
  )
  docker exec mandmandm-redis redis-cli -n 0 @CmdParts
}

Write-Host "==> 0) Asegurar que existen tablas y servicios (Postgres/Mongo/Redis ya deben estar levantados)."

Write-Host "==> 1) Seed de Usuario A en Postgres si no existe"
$existsA = Exec-PSQL -Sql "SELECT 1 FROM user_profiles WHERE id = '$userA_id' LIMIT 1;"
if (-not $existsA -or $existsA.Trim() -eq "") {
  Write-Host "   - Insertando user_profiles para user A"
  Exec-PSQL -Sql @"
INSERT INTO user_profiles (id, unique_id, oauth_provider, oauth_subject, email, full_name, picture, created_at)
VALUES (
  '$userA_id',
  '$userA_unique_id',
  '$userA_oauth_provider',
  '$userA_oauth_subject',
  '$userA_email',
  '$userA_full_name',
  '$userA_picture',
  NOW()
)
ON CONFLICT (id) DO NOTHING;
"@
} else {
  Write-Host "   - user A ya existe en Postgres"
}

Write-Host "==> 2) Crear Usuario B vía /users/oauth-sync"
$bodyB = @{
  provider = $provider
  subject = $subjectB
  email = $emailB
  full_name = $fullNameB
  picture = $pictureB
}
$bResp = Invoke-Api -Method Post -Path "/users/oauth-sync" -Body $bodyB
$userB_id = $bResp.id
$userB_unique_id = $bResp.unique_id
Write-Host "   - userB_id=$userB_id"
Write-Host "   - userB_unique_id=$userB_unique_id"

Write-Host "==> 3) Agregar contacto A -> B"
$bodyContact = @{ target_unique_id = $userB_unique_id }
Invoke-Api -Method Post -Path "/users/$userA_id/contacts" -Body $bodyContact | Out-Null

Write-Host "==> 4) Crear grupo /conversations/"
$conversationName = "G-e2e-" + ([guid]::NewGuid().ToString().Substring(0,8))
$conversationDescription = "e2e presence (redis) + conversations (mongo)"
$bodyConv = @{
  type = "group"
  name = $conversationName
  description = $conversationDescription
  created_by = $userA_id
  members = @($userB_id)
}
$convResp = Invoke-Api -Method Post -Path "/conversations/" -Body $bodyConv
$conversationId = $convResp.id
Write-Host "   - conversationId=$conversationId"

Write-Host "==> 5) Enviar mensaje (en este proyecto: recibos presencia en Redis)"
$messageId = [guid]::NewGuid().ToString()
$senderId = $userA_id
$recipientId = $userB_id

$bodySent = @{
  message_id = $messageId
  sender_id = $senderId
  recipient_id = $recipientId
}
Invoke-Api -Method Post -Path "/presence/messages" -Body $bodySent | Out-Null

$bodyDelivered = @{ recipient_id = $recipientId }
Invoke-Api -Method Post -Path "/presence/messages/$messageId/delivered" -Body $bodyDelivered | Out-Null

$bodyRead = @{ recipient_id = $recipientId }
Invoke-Api -Method Post -Path "/presence/messages/$messageId/read" -Body $bodyRead | Out-Null

$receiptsResp = Invoke-Api -Method Get -Path "/presence/messages/$messageId"
Write-Host "   - Receipts antes de borrar (espera READ):"
($receiptsResp | ConvertTo-Json -Depth 10)

Write-Host "==> 6) Verificación interna en Redis"
$status = Exec-Redis -CmdParts @("hget", "presence:receipt:${messageId}:${recipientId}", "status")
$deliveredAt = Exec-Redis -CmdParts @("hget", "presence:receipt:${messageId}:${recipientId}", "delivered_at")
$readAt = Exec-Redis -CmdParts @("hget", "presence:receipt:${messageId}:${recipientId}", "read_at")
$setMembers = Exec-Redis -CmdParts @("smembers", "presence:message_receipts:${messageId}")
Write-Host "   - Redis status=$status"
Write-Host "   - Redis delivered_at=$deliveredAt"
Write-Host "   - Redis read_at=$readAt"
Write-Host "   - Redis message_receipts set members=$setMembers"

Write-Host "==> 7) Borrar el mensaje (borrado de recibos en Redis; no existe endpoint HTTP de borrado hoy)"
$null = Exec-Redis -CmdParts @("del", "presence:receipt:${messageId}:${recipientId}")
$null = Exec-Redis -CmdParts @("srem", "presence:message_receipts:${messageId}", $recipientId)

$receiptsAfter = Invoke-Api -Method Get -Path "/presence/messages/$messageId"
Write-Host "   - Receipts después de borrar (espera lista vacía):"
($receiptsAfter | ConvertTo-Json -Depth 10)

Write-Host "==> 8) Eliminar contacto A -> B"
Invoke-Api -Method Delete -Path "/users/$userA_id/contacts/$userB_id" | Out-Null

Write-Host "==> 9) Verificación en Postgres de contactos"
$contacts = Exec-PSQL -Sql "SELECT owner_id, contact_id FROM user_profile_contacts WHERE (owner_id='$userA_id' AND contact_id='$userB_id') OR (owner_id='$userB_id' AND contact_id='$userA_id') ORDER BY owner_id, contact_id;"
Write-Host "   - Contacts link(s) entre A y B (debería ser vacío):"
Write-Host $contacts

Write-Host "==> 10) Eliminar grupo"
$bodyConvDel = @{ actor_id = $userA_id }
Invoke-Api -Method Delete -Path "/conversations/$conversationId" -Body $bodyConvDel | Out-Null

Write-Host "==> 11) Verificación en Mongo (conversation borrada)"
$mongoDoc = Exec-Mongo -Eval "db = db.getSiblingDB('groupsapp_messages'); printjson(db.conversations.findOne({id:'$conversationId'}));"
Write-Host $mongoDoc

Write-Host "==> 12) Eliminar usuario A"
Invoke-Api -Method Delete -Path "/users/$userA_id" | Out-Null

Write-Host "==> 13) Verificación en Postgres (user A borrado)"
$userAExists2 = Exec-PSQL -Sql "SELECT 1 FROM user_profiles WHERE id = '$userA_id' LIMIT 1;"
Write-Host "   - user A exists? " $userAExists2

Write-Host "==> FIN. Datos generados:"
Write-Host "   userA_id=$userA_id"
Write-Host "   userB_id=$userB_id"
Write-Host "   conversationId=$conversationId"
Write-Host "   messageId=$messageId"

