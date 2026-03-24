from dataclasses import replace
from app.domain.entities.user_profile import UserProfileEntityFactory
from app.domain.repositories.user_profile import UserProfileRepository
from app.domain.repositories.group import GroupRepository
from app.domain.use_cases.user_profile import UserProfileUseCases
from app.domain.exceptions import (
    UserProfileNotFound,
    ContactAlreadyExists,
    ContactNotFound,
    CannotAddSelfContact,
)


class UserProfileService(UserProfileUseCases):
    def __init__(self, user_profile_repository: UserProfileRepository, group_repository: GroupRepository):
        self.user_profile_repository = user_profile_repository
        self.group_repository = group_repository

    def upsert_oauth_profile(self, provider: str, subject: str, email: str, full_name: str, picture: str | None = None):
        existing = self.user_profile_repository.get_by_oauth(provider, subject)
        if existing is not None:
            updated = replace(existing, email=email.strip().lower(), full_name=(full_name or existing.full_name), picture=picture)
            return self.user_profile_repository.update(updated)
        profile = UserProfileEntityFactory.create(provider, subject, email, full_name, picture)
        return self.user_profile_repository.add(profile)

    def get_profile(self, profile_id: str):
        profile = self.user_profile_repository.get_by_id(profile_id)
        if profile is None:
            raise UserProfileNotFound()
        return profile

    def add_contact(self, owner_id: str, target_unique_id: str):
        owner = self.get_profile(owner_id)
        target = self.user_profile_repository.get_by_unique_id(target_unique_id)
        if target is None:
            raise UserProfileNotFound()
        if owner.id == target.id:
            raise CannotAddSelfContact()
        if target.id in owner.contacts:
            raise ContactAlreadyExists()
        owner = replace(owner, contacts=owner.contacts + [target.id])
        target_contacts = target.contacts if owner.id in target.contacts else target.contacts + [owner.id]
        target = replace(target, contacts=target_contacts)
        self.user_profile_repository.update(target)
        return self.user_profile_repository.update(owner)

    def remove_contact(self, owner_id: str, target_id: str):
        owner = self.get_profile(owner_id)
        target = self.get_profile(target_id)
        if target.id not in owner.contacts:
            raise ContactNotFound()
        owner = replace(owner, contacts=[c for c in owner.contacts if c != target.id])
        target = replace(target, contacts=[c for c in target.contacts if c != owner.id])
        self.user_profile_repository.update(target)
        return self.user_profile_repository.update(owner)

    def delete_account(self, owner_id: str) -> None:
        owner = self.get_profile(owner_id)
        # remove bidirectional contact links
        for contact_id in list(owner.contacts):
            contact = self.user_profile_repository.get_by_id(contact_id)
            if contact is not None:
                updated = replace(contact, contacts=[c for c in contact.contacts if c != owner.id])
                self.user_profile_repository.update(updated)
        # clean groups membership and delete owned groups
        for group in self.group_repository.list_all():
            if owner.id == group.created_by:
                self.group_repository.delete(group.id)
                continue
            if owner.id in group.members:
                new_members = [m for m in group.members if m != owner.id]
                new_admins = [a for a in group.admins if a != owner.id]
                if not new_members:
                    self.group_repository.delete(group.id)
                else:
                    if not new_admins:
                        new_admins = [new_members[0]]
                    self.group_repository.update(replace(group, members=new_members, admins=new_admins))
        self.user_profile_repository.delete(owner.id)
