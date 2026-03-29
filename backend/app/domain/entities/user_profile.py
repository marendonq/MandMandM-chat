from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class UserProfileEntity:
    id: str
    unique_id: str
    oauth_provider: str
    oauth_subject: str
    email: str
    full_name: str
    picture: str | None
    created_at: datetime
    contacts: list[str]


class UserProfileEntityFactory:
    @staticmethod
    def create(provider: str, subject: str, email: str, full_name: str, picture: str | None = None) -> UserProfileEntity:
        uid = str(uuid.uuid4())
        short = uid.split('-')[0]
        return UserProfileEntity(
            id=uid,
            unique_id=f"usr-{short}",
            oauth_provider=provider,
            oauth_subject=subject,
            email=email.strip().lower(),
            full_name=(full_name or '').strip() or 'Unknown User',
            picture=picture,
            created_at=datetime.utcnow(),
            contacts=[],
        )

    @staticmethod
    def create_password_profile(
        user_id: str,
        unique_phone_id: str,
        email: str,
        full_name: str,
    ) -> UserProfileEntity:
        """Perfil para registro email/contraseña: mismo id que auth_users; unique_id = teléfono normalizado."""
        return UserProfileEntity(
            id=user_id,
            unique_id=unique_phone_id,
            oauth_provider="password",
            oauth_subject=user_id,
            email=email.strip().lower(),
            full_name=(full_name or "").strip() or "Usuario",
            picture=None,
            created_at=datetime.utcnow(),
            contacts=[],
        )

    @staticmethod
    def create_oauth_with_phone(
        unique_phone_id: str,
        provider: str,
        oauth_subject: str,
        email: str,
        full_name: str,
        picture: str | None = None,
    ) -> UserProfileEntity:
        """OAuth (primer acceso): unique_id = teléfono normalizado; id nuevo UUID."""
        uid = str(uuid.uuid4())
        return UserProfileEntity(
            id=uid,
            unique_id=unique_phone_id,
            oauth_provider=provider,
            oauth_subject=str(oauth_subject),
            email=email.strip().lower(),
            full_name=(full_name or "").strip() or "OAuth User",
            picture=picture,
            created_at=datetime.utcnow(),
            contacts=[],
        )
