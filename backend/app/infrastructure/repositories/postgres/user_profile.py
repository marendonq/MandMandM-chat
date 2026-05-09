"""PostgreSQL implementation of the UserProfileRepository.

This module provides a production-ready repository for user profile data
using SQLAlchemy with PostgreSQL. Handles both profile data and contact
relationships stored in separate tables.
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.user_profile import UserProfileEntity
from app.domain.repositories.user_profile import UserProfileRepository
from app.infrastructure.database.models import UserProfileContactModel, UserProfileModel


class UserProfilePostgresRepository(UserProfileRepository):
    """PostgreSQL repository for UserProfileEntity.

    Uses SQLAlchemy ORM to persist user profile data and contact
    relationships in PostgreSQL. Contacts are stored in a separate
    table with a one-to-many relationship to the profile.
    """

    def __init__(self, session_factory: sessionmaker):
        """Initialize the PostgreSQL user profile repository.

        Args:
            session_factory: SQLAlchemy session factory for database access.
        """
        self._sf = session_factory

    def _session(self) -> Session:
        """Create a new database session.

        Returns:
            A new SQLAlchemy Session.
        """
        return self._sf()

    def _load_contacts(self, s: Session, profile_id: str) -> list[str]:
        """Load contact IDs for a given profile.

        Args:
            s: The current database session.
            profile_id: The ID of the profile to load contacts for.

        Returns:
            A list of contact user IDs.
        """
        rows = s.scalars(
            select(UserProfileContactModel.contact_id).where(UserProfileContactModel.owner_id == profile_id)
        ).all()
        return list(rows)

    def _replace_contacts(self, s: Session, profile_id: str, contact_ids: list[str]) -> None:
        """Replace all contacts for a profile with a new set.

        Deletes existing contacts and inserts the new ones.

        Args:
            s: The current database session.
            profile_id: The ID of the profile to update contacts for.
            contact_ids: The new list of contact user IDs.
        """
        s.execute(delete(UserProfileContactModel).where(UserProfileContactModel.owner_id == profile_id))
        for cid in contact_ids:
            s.add(UserProfileContactModel(owner_id=profile_id, contact_id=cid))

    def _to_entity(self, row: UserProfileModel, contacts: list[str]) -> UserProfileEntity:
        """Convert a database model to a UserProfileEntity.

        Args:
            row: The UserProfileModel from the database.
            contacts: List of contact user IDs for this profile.

        Returns:
            A UserProfileEntity constructed from the model data.
        """
        return UserProfileEntity(
            id=row.id,
            unique_id=row.unique_id,
            oauth_provider=row.oauth_provider,
            oauth_subject=row.oauth_subject,
            email=row.email,
            full_name=row.full_name,
            picture=row.picture,
            created_at=row.created_at,
            contacts=contacts,
        )

    def add(self, profile: UserProfileEntity) -> UserProfileEntity:
        """Persist a new user profile to PostgreSQL.

        Also stores the profile's contact relationships.

        Args:
            profile: The UserProfileEntity to persist.

        Returns:
            The persisted UserProfileEntity.
        """
        with self._session() as s:
            s.add(
                UserProfileModel(
                    id=profile.id,
                    unique_id=profile.unique_id,
                    oauth_provider=profile.oauth_provider,
                    oauth_subject=profile.oauth_subject,
                    email=profile.email,
                    full_name=profile.full_name,
                    picture=profile.picture,
                    created_at=profile.created_at,
                )
            )
            self._replace_contacts(s, profile.id, list(profile.contacts))
            s.commit()
        return profile

    def update(self, profile: UserProfileEntity) -> UserProfileEntity:
        """Update an existing user profile in PostgreSQL.

        Uses upsert behavior - inserts if the profile doesn't exist.
        Also replaces all contact relationships.

        Args:
            profile: The UserProfileEntity with updated data.

        Returns:
            The updated UserProfileEntity.
        """
        with self._session() as s:
            row = s.get(UserProfileModel, profile.id)
            if row is None:
                s.add(
                    UserProfileModel(
                        id=profile.id,
                        unique_id=profile.unique_id,
                        oauth_provider=profile.oauth_provider,
                        oauth_subject=profile.oauth_subject,
                        email=profile.email,
                        full_name=profile.full_name,
                        picture=profile.picture,
                        created_at=profile.created_at,
                    )
                )
            else:
                row.unique_id = profile.unique_id
                row.oauth_provider = profile.oauth_provider
                row.oauth_subject = profile.oauth_subject
                row.email = profile.email
                row.full_name = profile.full_name
                row.picture = profile.picture
            self._replace_contacts(s, profile.id, list(profile.contacts))
            s.commit()
        return profile

    def get_by_id(self, profile_id: str) -> UserProfileEntity | None:
        """Retrieve a user profile by its ID from PostgreSQL.

        Also loads the profile's contact relationships.

        Args:
            profile_id: The unique profile identifier.

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        with self._session() as s:
            row = s.get(UserProfileModel, profile_id)
            if row is None:
                return None
            contacts = self._load_contacts(s, profile_id)
            return self._to_entity(row, contacts)

    def get_by_unique_id(self, unique_id: str) -> UserProfileEntity | None:
        """Retrieve a user profile by its public unique ID (phone-based).

        Also loads the profile's contact relationships.

        Args:
            unique_id: The public unique identifier (e.g., normalized phone).

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        with self._session() as s:
            row = s.scalars(select(UserProfileModel).where(UserProfileModel.unique_id == unique_id)).first()
            if row is None:
                return None
            contacts = self._load_contacts(s, row.id)
            return self._to_entity(row, contacts)

    def get_by_oauth(self, provider: str, subject: str) -> UserProfileEntity | None:
        """Retrieve a user profile by OAuth provider and subject.

        Also loads the profile's contact relationships.

        Args:
            provider: The OAuth provider name (e.g., "google").
            subject: The OAuth subject identifier.

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        with self._session() as s:
            row = s.scalars(
                select(UserProfileModel).where(
                    UserProfileModel.oauth_provider == provider,
                    UserProfileModel.oauth_subject == subject,
                )
            ).first()
            if row is None:
                return None
            contacts = self._load_contacts(s, row.id)
            return self._to_entity(row, contacts)

    def list_all(self) -> list[UserProfileEntity]:
        """List all user profiles from PostgreSQL.

        Also loads contact relationships for each profile.

        Returns:
            A list of all UserProfileEntity objects.
        """
        with self._session() as s:
            rows = s.scalars(select(UserProfileModel)).all()
            return [self._to_entity(r, self._load_contacts(s, r.id)) for r in rows]

    def delete(self, profile_id: str) -> None:
        """Delete a user profile from PostgreSQL by its ID.

        Also deletes all contact relationships for the profile.

        Args:
            profile_id: The unique profile identifier to delete.
        """
        with self._session() as s:
            row = s.get(UserProfileModel, profile_id)
            if row is not None:
                s.delete(row)
            s.commit()
