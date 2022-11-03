# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL


from django.apps import AppConfig


# Override the default label to avoid duplicates
class WorkspaceRoleConfig(AppConfig):
    name = "taiga.workspaces.roles"
    label = "workspaces_roles"