# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

# Generated by Django 4.1 on 2022-08-09 12:02

import re

import django.contrib.auth.models
import django.contrib.postgres.fields.jsonb
import django.core.validators
import django.db.models.deletion
import taiga.base.db.models
import taiga.base.db.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=taiga.base.db.models.uuid_generator,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "username",
                    taiga.base.db.models.fields.LowerCharField(
                        help_text="Required. 255 characters or fewer. Letters, numbers and /./-/_ characters",
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[\\w.-]+$"),
                                "Enter a valid username.",
                                "invalid",
                            )
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    taiga.base.db.models.fields.LowerEmailField(
                        max_length=255, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Designates whether this user should be treated as active.",
                        verbose_name="active",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "full_name",
                    models.CharField(blank=True, max_length=256, null=True, verbose_name="full name"),
                ),
                (
                    "accepted_terms",
                    models.BooleanField(default=True, verbose_name="accepted terms"),
                ),
                (
                    "date_joined",
                    models.DateTimeField(auto_now_add=True, verbose_name="date joined"),
                ),
                (
                    "date_verification",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="date verification",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "ordering": ["username"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="AuthData",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        blank=True,
                        default=taiga.base.db.models.uuid_generator,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", taiga.base.db.models.fields.LowerSlugField(verbose_name="key")),
                ("value", models.CharField(max_length=300, verbose_name="value")),
                (
                    "extra",
                    django.contrib.postgres.fields.jsonb.JSONField(verbose_name="extra"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auth_data",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("key", "value")},
            },
        ),
    ]