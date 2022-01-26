# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

import random
from typing import List, Optional

from django.db import transaction
from faker import Faker
from fastapi import UploadFile
from taiga.permissions import choices
from taiga.projects import services as projects_services
from taiga.projects.models import Project
from taiga.roles import repositories as roles_repo
from taiga.roles.models import Role, WorkspaceRole
from taiga.users.models import User
from taiga.workspaces import services as workspaces_services
from taiga.workspaces.models import Workspace

fake: Faker = Faker()
Faker.seed(0)
random.seed(0)

################################
# CONFIGURATION
################################
NUM_USERS = 10
NUM_PROJECT_COLORS = 8
NUM_WORKSPACE_COLORS = 8
################################


@transaction.atomic
def load_sample_data() -> None:
    print("Loading sample data.")

    # USERS. Create users
    users = _create_users()

    # WORKSPACES
    # create one basic workspace and one premium workspace per user
    # admin role is created by deault
    # create members roles for premium workspaces
    workspaces = []
    for user in users:
        workspaces.append(_create_workspace(owner=user, is_premium=False))
        workspaces.append(_create_workspace(owner=user, is_premium=True))

    # create memberships for workspaces
    for workspace in workspaces:
        _create_workspace_memberships(workspace=workspace, users=users, except_for=workspace.owner)

    # PROJECTS
    projects = []
    for workspace in workspaces:
        # create one project (kanban) in each workspace with the same owner
        # it applies a template and creates also admin and general roles
        project = _create_project(workspace=workspace, owner=workspace.owner)

        # add other users to different roles (admin and general)
        _create_project_memberships(project=project, users=users, except_for=workspace.owner)

        projects.append(project)

    # CUSTOM PROJECTS
    custom_owner = users[0]
    workspace = _create_workspace(owner=custom_owner, name="Custom workspace")
    _create_empty_project(owner=custom_owner, workspace=workspace)
    _create_long_texts_project(owner=custom_owner, workspace=workspace)
    _create_inconsistent_permissions_project(owner=custom_owner, workspace=workspace)
    _create_project_with_several_roles(owner=custom_owner, workspace=workspace, users=users)
    _create_workspace_details()

    print("Sample data loaded.")


################################
# USERS
################################


def _create_users() -> List[User]:
    users = []
    for i in range(NUM_USERS):
        user = _create_user(index=i + 1)
        users.append(user)
    return users


def _create_user(index: int) -> User:
    username = f"user{index}"
    email = f"{username}@taiga.demo"
    full_name = fake.name()
    user = User.objects.create(username=username, email=email, full_name=full_name)
    user.set_password("123123")
    user.save()
    return user


################################
# ROLES
################################
# admin and general roles are automatically created with `_create_project`


def _create_project_role(project: Project, name: Optional[str] = None) -> Role:
    name = name or fake.word()
    return Role.objects.create(project=project, name=name, is_admin=False, permissions=choices.PROJECT_PERMISSIONS)


def _create_project_memberships(project: Project, users: List[User], except_for: User) -> None:
    # get admin and other roles
    admin_role = project.roles.get(slug="admin")
    other_roles = project.roles.exclude(slug="admin")

    # get users except the owner of the project
    other_users = [user for user in users if user.id != except_for.id]
    random.shuffle(other_users)

    # add 0, 1 or 2 other admins
    num_admins = random.randint(0, 2)
    for _ in range(num_admins):
        user = other_users.pop(0)
        roles_repo.create_membership(user=user, project=project, role=admin_role, email=user.email)

    # add other members in the different roles
    num_members = random.randint(0, len(other_users))
    for _ in range(num_members):
        user = other_users.pop(0)
        role = random.choice(other_roles)
        roles_repo.create_membership(user=user, project=project, role=role, email=user.email)


def _create_workspace_role(workspace: Workspace) -> WorkspaceRole:
    return WorkspaceRole.objects.create(
        workspace=workspace, name="Members", is_admin=False, permissions=choices.WORKSPACE_PERMISSIONS
    )


def _create_workspace_memberships(workspace: Workspace, users: list[User], except_for: User) -> None:
    # get admin and other roles
    admin_role = workspace.workspace_roles.get(slug="admin")
    other_roles = workspace.workspace_roles.exclude(slug="admin")

    # get users except the owner of the project
    other_users = [user for user in users if user.id != except_for.id]
    random.shuffle(other_users)

    # add 0, 1 or 2 other admins
    num_admins = random.randint(0, 2)
    for _ in range(num_admins):
        user = other_users.pop(0)
        roles_repo.create_workspace_membership(user=user, workspace=workspace, workspace_role=admin_role)

    # add other members in the different roles if any
    if other_roles:
        num_members = random.randint(0, len(other_users))
        for _ in range(num_members):
            user = other_users.pop(0)
            role = random.choice(other_roles)
            roles_repo.create_workspace_membership(user=user, workspace=workspace, workspace_role=role)


################################
# WORKSPACES
################################


def _create_workspace(
    owner: User, name: Optional[str] = None, color: Optional[int] = None, is_premium: Optional[bool] = False
) -> Workspace:
    name = name or fake.bs()[:35]
    if is_premium:
        name = f"{name}(P)"
    color = color or fake.random_int(min=1, max=NUM_WORKSPACE_COLORS)
    workspace = workspaces_services.create_workspace(name=name, owner=owner, color=color)
    if is_premium:
        workspace.is_premium = True
        # create non-admin role
        _create_workspace_role(workspace=workspace)
        workspace.save()
    return workspace


################################
# PROJECTS
################################


def _create_project(
    workspace: Workspace, owner: User, name: Optional[str] = None, description: Optional[str] = None
) -> Project:
    name = name or fake.catch_phrase()
    description = description or fake.paragraph(nb_sentences=2)
    with open("src/taiga/base/utils/sample_data/logo.png", "rb") as png_image_file:
        logo_file = UploadFile(file=png_image_file, filename="Logo")

        project = projects_services.create_project(
            name=name,
            description=description,
            color=fake.random_int(min=1, max=NUM_PROJECT_COLORS),
            owner=owner,
            workspace=workspace,
            logo=logo_file,
        )

    return project


################################
# CUSTOM PROJECTS
################################


def _create_empty_project(owner: User, workspace: Workspace) -> None:
    projects_services.create_project(
        name="Empty project",
        description=fake.paragraph(nb_sentences=2),
        color=fake.random_int(min=1, max=NUM_PROJECT_COLORS),
        owner=owner,
        workspace=workspace,
    )


def _create_long_texts_project(owner: User, workspace: Workspace) -> None:
    _create_project(
        owner=owner,
        workspace=workspace,
        name=f"Long texts project: { fake.sentence(nb_words=10) } ",
        description=fake.paragraph(nb_sentences=8),
    )


def _create_inconsistent_permissions_project(owner: User, workspace: Workspace) -> None:
    # give general role less permissions than public-permissions
    project = _create_project(
        name="Inconsistent Permissions",
        owner=owner,
        workspace=workspace,
    )
    general_members_role = project.roles.get(slug="general")
    general_members_role.permissions = ["view_us", "view_tasks"]
    general_members_role.save()
    project.public_permissions = choices.PROJECT_PERMISSIONS
    project.save()


def _create_project_with_several_roles(owner: User, workspace: Workspace, users: list[User]) -> None:
    project = _create_project(name="Several Roles", owner=owner, workspace=workspace)
    _create_project_role(project=project, name="UX/UI")
    _create_project_role(project=project, name="Developer")
    _create_project_role(project=project, name="Stakeholder")
    _create_project_memberships(project=project, users=users, except_for=project.owner)


def _create_workspace_details() -> None:
    user1000 = _create_user(1000)
    user1001 = _create_user(1001)

    # workspace premium, user1001 is ws-member
    workspace = _create_workspace(owner=user1000, is_premium=True, name="u1001 is ws member")
    members_role = workspace.workspace_roles.exclude(is_admin=True).first()
    roles_repo.create_workspace_membership(user=user1001, workspace=workspace, workspace_role=members_role)
    # user1001 is pj-member
    project = _create_project(workspace=workspace, owner=user1000, name="user1001 is pj member")
    members_role = project.roles.get(slug="general")
    roles_repo.create_membership(user=user1001, project=project, role=members_role)
    # user1001 is not a pj-member but the project allows 'view_us' to ws-members
    project = _create_project(workspace=workspace, owner=user1000, name="ws members allowed")
    project.workspace_member_permissions = ["view_us"]
    project.save()
    # user1001 is not a pj-member and ws-members are not allowed
    _create_project(workspace=workspace, owner=user1000, name="ws members not allowed")
    # user1001 is pj-member but its role has no-access
    project = _create_project(workspace=workspace, owner=user1000, name="user1001 has role no-access")
    members_role = project.roles.get(slug="general")
    roles_repo.create_membership(user=user1001, project=project, role=members_role)
    members_role.permissions = []
    members_role.save()
    # user1001 is a pj-owner
    _create_project(workspace=workspace, owner=user1001, name="user1001 is pj-owner")

    # workspace premium, user1001 is ws-member
    workspace = _create_workspace(owner=user1000, is_premium=True, name="u1001 is ws member, hasProjects:T")
    members_role = workspace.workspace_roles.exclude(is_admin=True).first()
    roles_repo.create_workspace_membership(user=user1001, workspace=workspace, workspace_role=members_role)
    # user1001 is not a pj-member and ws-members are not allowed
    _create_project(workspace=workspace, owner=user1000)

    # workspace premium, user1001 is ws-member
    workspace = _create_workspace(owner=user1000, is_premium=True, name="u1001 is ws member, hasProjects:F")
    members_role = workspace.workspace_roles.exclude(is_admin=True).first()
    roles_repo.create_workspace_membership(user=user1001, workspace=workspace, workspace_role=members_role)

    # workspace premium, user1001 is ws-member
    workspace = _create_workspace(owner=user1000, is_premium=True, name="u1001 ws-member, pj-mmbr vs ws-mmbr")
    members_role = workspace.workspace_roles.exclude(is_admin=True).first()
    roles_repo.create_workspace_membership(user=user1001, workspace=workspace, workspace_role=members_role)
    # user1001 is pj-member
    project = _create_project(workspace=workspace, owner=user1000, name="user1001 is pj member")
    members_role = project.roles.get(slug="general")
    roles_repo.create_membership(user=user1001, project=project, role=members_role)
    # user1001 is pj-member but its role has no-access, ws-members have permissions
    project = _create_project(workspace=workspace, owner=user1000, name="u1001 no-access, ws-member has perm")
    members_role = project.roles.get(slug="general")
    roles_repo.create_membership(user=user1001, project=project, role=members_role)
    members_role.permissions = []
    members_role.save()
    project.workspace_member_permissions = ["view_us"]
    project.save()
