/**
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Copyright (c) 2021-present Kaleidos Ventures SL
 */

import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { Store } from '@ngrx/store';
import { Project, Role, User } from '@taiga/data';
import { initRolesPermissions } from '~/app/modules/project/settings/feature-roles-permissions/+state/actions/roles-permissions.actions';
import { fetchMyContacts } from '~/app/shared/invite-to-project/data-access/+state/actions/invitation.action';
import {
  selectContacts,
  selectMemberRolesOrdered,
  selectUsersToInvite,
} from '~/app/shared/invite-to-project/data-access/+state/selectors/project.selectors';
import { BehaviorSubject, Observable } from 'rxjs';
import { skip, switchMap } from 'rxjs/operators';

interface Invitation {
  email: string;
  role: string;
}
@Component({
  selector: 'tg-invite-to-project',
  templateUrl: './invite-to-project.component.html',
  styleUrls: [
    './styles/invite-to-project.shared.css',
    './invite-to-project.component.css',
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteToProjectComponent implements OnInit {
  @Input()
  public project!: Project;

  @Output()
  public finishNewProject = new EventEmitter<Invitation[]>();

  @Output()
  public closeModal = new EventEmitter();

  public regexpEmail = /\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,4})+/g;
  public inviteEmails = '';
  public inviteEmailsErrors: {
    required: boolean;
    regex: boolean;
    listEmpty: boolean;
    peopleNotAdded: boolean;
    bulkError: boolean;
    moreThanFifty: boolean;
  } = {
    required: false,
    regex: false,
    listEmpty: false,
    peopleNotAdded: false,
    bulkError: false,
    moreThanFifty: false,
  };
  public inviteProjectForm: FormGroup = this.fb.group({
    users: new FormArray([]),
  });
  public orderedRoles!: Role[] | null;

  public validEmails$ = new BehaviorSubject([] as string[]);
  public memberRoles$ = this.store.select(selectMemberRolesOrdered);
  public contacts$ = this.store.select(selectContacts);
  public usersToInvite$!: Observable<Partial<User>[]>;

  constructor(private fb: FormBuilder, private store: Store) {}

  public get users() {
    return (this.inviteProjectForm.controls['users'] as FormArray)
      .controls as FormGroup[];
  }

  public get validEmails() {
    return this.validEmails$.value;
  }

  public get validInviteEmails() {
    return this.inviteEmails.match(this.regexpEmail) || [];
  }

  public ngOnInit() {
    this.usersToInvite$ = this.validEmails$.pipe(
      switchMap((validEmails) => {
        return this.store
          .select(selectUsersToInvite(validEmails))
          .pipe(skip(1));
      })
    );
    this.store.dispatch(initRolesPermissions({ project: this.project }));

    // when we add users to invite its necessary to add the result to the form
    this.usersToInvite$.subscribe((userToInvite) => {
      userToInvite.forEach((user) => {
        const userAlreadyExist = this.users?.find((it: FormGroup) => {
          return (it.value as Partial<User>).email === user.email;
        });
        !userAlreadyExist && this.users.push(this.fb.group(user));
      });
      this.inviteEmails = '';
      this.inviteEmailsChange('');
    });

    this.memberRoles$.subscribe((memberRoles) => {
      this.orderedRoles = memberRoles;
    });
  }

  public emailsWithoutDuplications() {
    const emails = this.validInviteEmails;
    return emails?.filter((email, i) => emails.indexOf(email) === i);
  }

  public trackByIndex(index: number) {
    return index;
  }

  public resetErrors() {
    this.inviteEmailsErrors = {
      required: false,
      regex: false,
      listEmpty: false,
      peopleNotAdded: false,
      bulkError: false,
      moreThanFifty: false,
    };
  }

  public inviteEmailsChange(value: string) {
    const result = value.match(this.regexpEmail) || [];
    this.validEmails$.next([...result]);
  }

  public addUser() {
    const emailRgx = this.regexpEmail.test(this.inviteEmails);
    const bulkErrors = this.inviteEmails
      .replace(this.regexpEmail, '')
      .replace(/[;,\s\n]/g, '');
    this.resetErrors();
    if (this.inviteEmails === '') {
      this.inviteEmailsErrors.required = true;
    } else if (!emailRgx) {
      this.inviteEmailsErrors.regex = true;
    } else if (bulkErrors) {
      this.inviteEmailsErrors.bulkError = true;
    } else {
      this.inviteEmailsChange(this.inviteEmails);
      this.store.dispatch(fetchMyContacts({ emails: this.validEmails }));
    }
  }

  public deleteUser(i: number) {
    (this.inviteProjectForm.controls['users'] as FormArray).removeAt(i);
  }

  public getRoleSlug(roleName: string) {
    return this.orderedRoles?.find((role) => role.name === roleName);
  }

  public generatePayload(): Invitation[] {
    return this.users.map((user) => {
      return {
        email: user.get('email')?.value as string,
        role: this.getRoleSlug(user.get('roles')?.value as string)?.slug || '',
      };
    });
  }

  public sendForm() {
    this.resetErrors();
    if (this.users.length > 50) {
      this.inviteEmailsErrors.moreThanFifty = true;
    } else if (this.users.length) {
      this.finishNewProject.next(this.generatePayload());
      this.close();
    } else {
      this.inviteEmailsErrors.listEmpty = true;
    }
    this.inviteEmailsErrors.peopleNotAdded = !!this.inviteEmails;
  }

  public close() {
    this.closeModal.next();
  }
}