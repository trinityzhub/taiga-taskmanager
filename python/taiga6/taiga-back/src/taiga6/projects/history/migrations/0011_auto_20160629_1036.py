# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL

# Generated by Django 1.9.2 on 2016-06-29 10:36
from __future__ import unicode_literals

from django.db import migrations, connection
from taiga6.projects.history.services import get_instance_from_key


GENERATE_CORRECT_HISTORY_ENTRIES_TABLE = """
    -- Creating a table containing all the existing object keys and the project ids
    DROP TABLE IF EXISTS project_keys;
    CREATE TABLE project_keys (
    	key VARCHAR,
    	project_id INTEGER
    );

    DROP INDEX IF EXISTS project_keys_index;
    CREATE INDEX project_keys_index
      ON project_keys
      USING btree
      (key);

    INSERT INTO project_keys
    SELECT 'milestones.milestone:' || id, project_id
    FROM milestones_milestone;

    INSERT INTO project_keys
    SELECT 'userstories.userstory:' || id, project_id
    FROM userstories_userstory;

    INSERT INTO project_keys
    SELECT 'tasks.task:' || id, project_id
    FROM tasks_task;

    INSERT INTO project_keys
    SELECT 'issues.issue:' || id, project_id
    FROM issues_issue;

    INSERT INTO project_keys
    SELECT 'wiki.wikipage:' || id, project_id
    FROM wiki_wikipage;

    INSERT INTO project_keys
    SELECT 'projects.project:' || id, id
    FROM projects_project;

    -- Create a table where we will insert all the history_historyentry content with its correct project_id
    -- Elements without project_id won't be inserted
    DROP TABLE IF EXISTS history_historyentry_correct;
    CREATE TABLE history_historyentry_correct AS
    SELECT
    	history_historyentry.id ,
    	history_historyentry.user,
    	history_historyentry.created_at,
    	history_historyentry.type,
    	history_historyentry.is_snapshot,
    	history_historyentry.key,
    	history_historyentry.diff,
    	history_historyentry.snapshot,
    	history_historyentry.values,
    	history_historyentry.comment,
    	history_historyentry.comment_html,
    	history_historyentry.delete_comment_date,
    	history_historyentry.delete_comment_user,
    	history_historyentry.is_hidden,
    	history_historyentry.comment_versions,
    	history_historyentry.edit_comment_date,
    	project_keys.project_id
    FROM history_historyentry
    INNER JOIN project_keys
    ON project_keys.key = history_historyentry.key;

    -- Delete aux table
    DROP TABLE IF EXISTS project_keys;
    """

def get_constraints_def_sql(table_name):
    cursor = connection.cursor()
    query = """
        SELECT 'ALTER TABLE "'||nspname||'"."'||relname||'" ADD CONSTRAINT "'||conname||'" '||
           pg_get_constraintdef(pg_constraint.oid)||';'
        FROM pg_constraint
        INNER JOIN pg_class ON conrelid=pg_class.oid
        INNER JOIN pg_namespace ON pg_namespace.oid=pg_class.relnamespace
        WHERE relname='{}'
        ORDER BY CASE WHEN contype='f' THEN 0 ELSE 1 END DESC,contype DESC,nspname DESC,relname DESC,conname DESC;
    """.format(table_name)
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def get_indexes_def_sql(table_name):
    cursor = connection.cursor()
    query = """
        SELECT pg_get_indexdef(idx.oid)||';'
        FROM pg_index ind
          JOIN pg_class idx ON idx.oid = ind.indexrelid
          JOIN pg_class tbl ON tbl.oid = ind.indrelid
          LEFT JOIN pg_namespace ns ON ns.oid = tbl.relnamespace
        WHERE
          tbl.relname = '{}' AND
          indisprimary=FALSE;
    """.format(table_name)
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def drop_constraints(table_name):
    # This query returns all the ALTER sentences needed to drop the constraints
    cursor = connection.cursor()
    alter_sentences_query = """
        SELECT 'ALTER TABLE "'||nspname||'"."'||relname||'" DROP CONSTRAINT "'||conname||'" '||';'
        FROM pg_constraint
        INNER JOIN pg_class ON conrelid=pg_class.oid
        INNER JOIN pg_namespace ON pg_namespace.oid=pg_class.relnamespace
        WHERE relname='{}'
        ORDER BY CASE WHEN contype='f' THEN 0 ELSE 1 END DESC,contype DESC,nspname DESC,relname DESC,conname DESC;
    """.format(table_name)
    cursor.execute(alter_sentences_query)
    alter_sentences = [row[0] for row in cursor.fetchall()]

    #Now we execute those sentences
    for alter_sentence in alter_sentences:
        cursor.execute(alter_sentence)


def toggle_history_entries_tables(apps, schema_editor):
    history_entry_sql_def_contraints = get_constraints_def_sql("history_historyentry")
    history_entry_sql_def_indexes = get_indexes_def_sql("history_historyentry")
    history_change_notifications_sql_def_contraints = get_constraints_def_sql("notifications_historychangenotification_history_entries")
    drop_constraints("notifications_historychangenotification_history_entries")
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM notifications_historychangenotification_history_entries;
        DROP TABLE history_historyentry;
        ALTER TABLE "history_historyentry_correct" RENAME to "history_historyentry";
    """)

    for history_entry_sql_def_contraint in history_entry_sql_def_contraints:
            cursor.execute(history_entry_sql_def_contraint)

    for history_entry_sql_def_index in history_entry_sql_def_indexes:
            cursor.execute(history_entry_sql_def_index)

    # Restoring the dropped constraints and indexes
    for history_change_notifications_sql_def_contraint in history_change_notifications_sql_def_contraints:
            cursor.execute(history_change_notifications_sql_def_contraint)


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0010_historyentry_project'),
        ('wiki', '0003_auto_20160615_0721'),
        ('users', '0022_auto_20160629_1443')
    ]

    operations = [
        migrations.RunSQL(GENERATE_CORRECT_HISTORY_ENTRIES_TABLE),
        migrations.RunPython(toggle_history_entries_tables)
    ]
