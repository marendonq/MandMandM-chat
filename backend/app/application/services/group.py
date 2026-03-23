from dataclasses import replace
from app.domain.entities.group import GroupEntityFactory
from app.domain.exceptions import (
    GroupNotFound,
    UserAlreadyInGroup,
    UserNotInGroup,
    UnauthorizedGroupAction,
    CannotRemoveLastAdmin,
)
from app.domain.repositories.group import GroupRepository
from app.domain.use_cases.group import GroupUseCases


class GroupService(GroupUseCases):
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository

    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None):
        return self.group_repository.add(
            GroupEntityFactory.create(name=name, description=description, created_by=created_by, members=members)
        )

    def list_groups(self):
        return self.group_repository.list_all()

    def get_group(self, group_id: str):
        group = self.group_repository.get_by_id(group_id)
        if group is None:
            raise GroupNotFound()
        return group

    def add_user_to_group(self, group_id: str, actor_id: str, user_id: str):
        group = self.get_group(group_id)
        if actor_id not in group.members:
            raise UnauthorizedGroupAction("Only group members can add users")
        if user_id in group.members:
            raise UserAlreadyInGroup()
        updated = replace(group, members=group.members + [user_id])
        return self.group_repository.update(updated)

    def delete_user_from_group(self, group_id: str, actor_id: str, user_id: str):
        group = self.get_group(group_id)
        if actor_id not in group.admins:
            raise UnauthorizedGroupAction("Only admins can remove users")
        if user_id not in group.members:
            raise UserNotInGroup()
        new_members = [member for member in group.members if member != user_id]
        new_admins = [admin for admin in group.admins if admin != user_id]
        if not new_admins:
            raise CannotRemoveLastAdmin()
        updated = replace(group, members=new_members, admins=new_admins)
        return self.group_repository.update(updated)

    def update_admin(self, group_id: str, actor_id: str, user_id: str):
        group = self.get_group(group_id)
        if actor_id not in group.admins:
            raise UnauthorizedGroupAction("Only admins can assign admins")
        if user_id not in group.members:
            raise UserNotInGroup()
        if user_id in group.admins:
            return group
        updated = replace(group, admins=group.admins + [user_id])
        return self.group_repository.update(updated)

    def exit_group(self, group_id: str, user_id: str):
        group = self.get_group(group_id)
        if user_id not in group.members:
            raise UserNotInGroup()
        new_members = [member for member in group.members if member != user_id]
        new_admins = [admin for admin in group.admins if admin != user_id]
        if not new_admins:
            raise CannotRemoveLastAdmin()
        updated = replace(group, members=new_members, admins=new_admins)
        return self.group_repository.update(updated)
