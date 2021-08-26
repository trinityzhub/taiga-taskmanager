# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from taiga6.base.utils.time import timestamp_ms
from taiga6.projects.due_dates.models import DueDateMixin
from taiga6.projects.occ import OCCModelMixin
from taiga6.projects.notifications.mixins import WatchedModelMixin
from taiga6.projects.mixins.blocked import BlockedMixin
from taiga6.projects.tagging.models import TaggedMixin


class Task(OCCModelMixin, WatchedModelMixin, BlockedMixin, TaggedMixin, DueDateMixin, models.Model):
    user_story = models.ForeignKey(
        "userstories.UserStory",
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("user story"),
        on_delete=models.CASCADE,
    )
    ref = models.BigIntegerField(db_index=True, null=True, blank=True, default=None,
                                 verbose_name=_("ref"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        default=None,
        related_name="owned_tasks",
        verbose_name=_("owner"),
        on_delete=models.SET_NULL,
    )
    status = models.ForeignKey(
        "projects.TaskStatus",
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name=_("status"),
        on_delete=models.SET_NULL,
    )
    project = models.ForeignKey(
        "projects.Project",
        null=False,
        blank=False,
        related_name="tasks",
        verbose_name=_("project"),
        on_delete=models.CASCADE,
    )
    milestone = models.ForeignKey(
        "milestones.Milestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        default=None,
        related_name="tasks",
        verbose_name=_("milestone")
    )
    created_date = models.DateTimeField(null=False, blank=False,
                                        verbose_name=_("created date"),
                                        default=timezone.now)
    modified_date = models.DateTimeField(null=False, blank=False,
                                         verbose_name=_("modified date"))
    finished_date = models.DateTimeField(null=True, blank=True,
                                         verbose_name=_("finished date"))
    subject = models.TextField(null=False, blank=False,
                               verbose_name=_("subject"))

    us_order = models.BigIntegerField(null=False, blank=False, default=timestamp_ms,
                                        verbose_name=_("us order"))
    taskboard_order = models.BigIntegerField(null=False, blank=False, default=timestamp_ms,
                                          verbose_name=_("taskboard order"))

    description = models.TextField(null=False, blank=True, verbose_name=_("description"))
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        default=None,
        related_name="tasks_assigned_to_me",
        verbose_name=_("assigned to"),
        on_delete=models.SET_NULL,
    )
    attachments = GenericRelation("attachments.Attachment")
    is_iocaine = models.BooleanField(default=False, null=False, blank=True,
                                     verbose_name=_("is iocaine"))
    external_reference = ArrayField(models.TextField(null=False, blank=False),
                                    null=True, blank=True, default=None, verbose_name=_("external reference"))
    _importing = None

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"
        ordering = ["project", "created_date", "ref"]
        # unique_together = ("ref", "project")

    def save(self, *args, **kwargs):
        if not self._importing or not self.modified_date:
            self.modified_date = timezone.now()

        if not self.status:
            self.status = self.project.default_task_status

        return super().save(*args, **kwargs)

    def __str__(self):
        return "({1}) {0}".format(self.ref, self.subject)

    @property
    def is_closed(self):
        return self.status is not None and self.status.is_closed
