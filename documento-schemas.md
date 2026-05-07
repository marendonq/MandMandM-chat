# Estructuras de Schemas - MandMandM

Este documento resume las estructuras de datos definidas en `backend/app/infrastructure/schemas`.

## Auth (`auth.py`)

### `RegisterRequest`
- `email: EmailStr`
- `password: str` (min_length=8)
- `full_name: str` (min_length=1)
- `phone: str` (min_length=1)

### `LoginRequest`
- `email: EmailStr`
- `password: str` (min_length=8)

### `UserSchema`
- `id: str`
- `email: str`
- `password_hash: str`
- `full_name: str`
- `created_at: datetime`

### `RegisterResponse`
- `access_token: str`
- `user: UserSchema`
- `unique_id: str`

### `LoginResponse`
- `access_token: str`

## User Profile (`user_profile.py`)

### `UserProfileResponse`
- `id: str`
- `unique_id: str`
- `oauth_provider: str`
- `oauth_subject: str`
- `email: str`
- `full_name: str`
- `picture: str | None`
- `created_at: datetime`
- `contacts: list[str]`

### `AddContactRequest`
- `target_unique_id: str`

## Conversations (`conversation.py`)

### `ConversationType` (Enum)
- `PRIVATE = "private"`
- `GROUP = "group"`

### `ConversationCreateRequest`
- `type: ConversationType`
- `name: str | None`
- `description: str | None`
- `created_by: str`
- `members: list[str]` (default `[]`)
- `participant_two: str | None`

### `PrivateConversationCreateRequest`
- `created_by: str`
- `participant_two: str`

### `AddUserToConversationRequest`
- `actor_id: str`
- `user_id: str`

### `UpdateAdminRequest`
- `actor_id: str`
- `user_id: str`

### `ConversationDeleteRequest`
- `actor_id: str`

### `ConversationResponse`
- `id: str`
- `type: ConversationType`
- `name: str | None`
- `description: str | None`
- `created_by: str`
- `created_at: datetime`
- `members: list[str]`
- `admins: list[str] | None`
- `invitation_link: str | None`

## Messages (`message.py`)

### `MessageCreateRequest`
- `conversation_id: str` (min_length=1)
- `sender_id: str` (min_length=1)
- `content: str` (min_length=1, max_length=4000)
- Validador: no permite contenido vacio o solo espacios.

### `FileMessageCreateRequest`
- `conversation_id: str` (min_length=1)
- `sender_id: str` (min_length=1)
- `file_id: str` (min_length=1)
- `content: str | None` (default `""`, max_length=4000)
- Validador: `file_id` no vacio.

### `MessageEditRequest`
- `user_id: str` (min_length=1)
- `new_content: str` (min_length=1, max_length=4000)
- Validador: no permite contenido vacio o solo espacios.

### `MessageDeleteRequest`
- `user_id: str` (min_length=1)

### `MessageListRequest`
- `conversation_id: str` (min_length=1)
- `limit: int` (default=50, ge=1, le=100)
- `before: datetime | None`

### `MessageResponse`
- `id: str`
- `conversation_id: str`
- `sender_id: str`
- `content: str`
- `message_type: str`
- `file_id: str | None`
- `created_at: datetime`
- `updated_at: datetime | None`
- `is_deleted: bool` (default `False`)

### `MessageListResponse`
- `messages: list[MessageResponse]`
- `total: int`
- `has_more: bool`

### `MessageCreateResponse`
- `message: MessageResponse`
- `receipt_status: str | None`

### `MessageDeletedResponse`
- `message_id: str`
- `status: str` (default `"deleted"`)

### `MessageUpdatedResponse`
- `message: MessageResponse`

## Presence (`presence.py`)

### `HeartbeatRequest`
- `user_id: str` (min_length=1)

### `UserPresenceResponse`
- `user_id: str`
- `activity_status: str`
- `last_interaction_at: datetime | None`
- `offline_since: datetime | None`

### `MessageReceiptRegisterRequest`
- `message_id: str` (min_length=1)
- `sender_id: str` (min_length=1)
- `recipient_id: str` (min_length=1)

### `RecipientActionRequest`
- `recipient_id: str` (min_length=1)

### `MessageReceiptResponse`
- `message_id: str`
- `sender_id: str`
- `recipient_id: str`
- `status: str`
- `sent_at: datetime`
- `delivered_at: datetime | None`
- `read_at: datetime | None`

### `MessageReceiptsForMessageResponse`
- `message_id: str`
- `receipts: list[MessageReceiptResponse]`

## Notifications (`notification.py`)

### `NotificationCreateRequest`
- `user_id: str`
- `type: str`
- `content: str`
- `status: str | None`

### `NotificationResponse`
- `id: str`
- `user_id: str`
- `type: str`
- `content: str`
- `status: str`
- `created_at: datetime`
- `read_at: datetime | None`

## Files (`file.py`)

### `FileResponse`
- `id: str`
- `file_name: str`
- `file_type: str`
- `uploader_id: str`
- `storage_path: str`
- `created_at: datetime`
- `file_size: int | None`
- `message_id: str | None`
- `thumbnail_path: str | None`

### `FileUploadRequest`
- `file_name: str`
- `file_type: str`
- `uploader_id: str`
- `message_id: str`

### `FileDeleteRequest`
- `file_id: str`

## File Metadata (`file_asset.py`)

### `FileAssetRegisterRequest`
- `owner_profile_id: str` (min_length=1)
- `original_name: str` (min_length=1)
- `mime_type: str` (default `""`)
- `size_bytes: int` (ge=0)
- `storage_key: str` (min_length=1)

### `FileAssetResponse`
- `id: str`
- `owner_profile_id: str`
- `original_name: str`
- `mime_type: str`
- `size_bytes: int`
- `storage_key: str`
- `created_at: datetime`

### `FileAssetListResponse`
- `items: list[FileAssetResponse]`

## File Images (`file-images.py`)

### `FileImage`
- `id: int`
- `uploaded_by: str`
- `file_name: str`
- `size: int`
- `content_type: str`
- `category: str`
- `created_at: str`

## Nota

- El archivo `backend/app/infrastructure/schemas/messages.py` existe pero esta vacio.
- Para los detalles exactos de ejemplos JSON y tipos serializados, puedes validar en `/docs`.
