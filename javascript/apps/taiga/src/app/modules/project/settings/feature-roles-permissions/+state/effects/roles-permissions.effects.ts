/**
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Copyright (c) 2021-present Kaleidos Ventures SL
 */

import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';

import { filter, map } from 'rxjs/operators';

import * as ProjectActions from '../actions/roles-permissions.actions';
import { ProjectApiService } from '@taiga/api';
import { AppService } from '~/app/services/app.service';
import { fetch, pessimisticUpdate } from '@nrwl/angular';
import { HttpErrorResponse } from '@angular/common/http';

@Injectable()
export class RolesPermissionsEffects {
  public loadMemberRoles$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.initRolesPermissions),
      fetch({
        run: (action) => {
          return this.projectApiService
            .getMemberRoles(action.project.slug)
            .pipe(
              map((roles) => {
                return ProjectActions.fetchMemberRolesSuccess({ roles });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            return this.appService.toastError(httpResponse, {
              label: 'errors.member_roles',
              message: 'errors.please_refresh',
            });
          } else {
            return this.appService.errorManagement(httpResponse);
          }
        },
      })
    );
  });

  public loadPublicPermissions$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.initRolesPermissions),
      fetch({
        run: (action) => {
          return this.projectApiService
            .getPublicPermissions(action.project.slug)
            .pipe(
              map((permissions) => {
                return ProjectActions.fetchPublicPermissionsSuccess({
                  permissions: permissions,
                });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            return this.appService.toastError(httpResponse, {
              label: 'errors.public_permissions',
              message: 'errors.please_refresh',
            });
          } else {
            return this.appService.errorManagement(httpResponse);
          }
        },
      })
    );
  });

  public loadWorkspacePermissions$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.initRolesPermissions),
      filter((action) => action.project.workspace.isPremium),
      fetch({
        run: (action) => {
          return this.projectApiService
            .getworkspacePermissions(action.project.slug)
            .pipe(
              map((permissions) => {
                return ProjectActions.fetchWorkspacePermissionsSuccess({
                  permissions,
                });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            return this.appService.toastError(httpResponse, {
              label: 'errors.workspace_permissions',
              message: 'errors.please_refresh',
            });
          } else {
            return this.appService.errorManagement(httpResponse);
          }
        },
      })
    );
  });

  public updateRolePermissions$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.updateRolePermissions),
      pessimisticUpdate({
        run: (action) => {
          return this.projectApiService
            .putMemberRoles(action.project, action.roleSlug, action.permissions)
            .pipe(
              map((role) => {
                return ProjectActions.updateRolePermissionsSuccess({ role });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            this.appService.toastError(httpResponse, {
              label: 'errors.save_changes',
              message: 'errors.please_refresh',
            });
          } else {
            this.appService.errorManagement(httpResponse);
          }
          return ProjectActions.updateRolePermissionsError();
        },
      })
    );
  });

  public updatePublicPermissions$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.updatePublicPermissions),
      pessimisticUpdate({
        run: (action) => {
          return this.projectApiService
            .putPublicPermissions(action.project, action.permissions)
            .pipe(
              map((permissions) => {
                return ProjectActions.updatePublicPermissionsSuccess({
                  permissions,
                });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            this.appService.toastError(httpResponse, {
              label: 'errors.save_changes',
              message: 'errors.please_refresh',
            });
          } else {
            this.appService.errorManagement(httpResponse);
          }
          return ProjectActions.updateRolePermissionsError();
        },
      })
    );
  });

  public updateWorkspacePermissions$ = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProjectActions.updateWorkspacePermissions),
      pessimisticUpdate({
        run: (action) => {
          return this.projectApiService
            .putworkspacePermissions(action.project, action.permissions)
            .pipe(
              map((permissions) => {
                return ProjectActions.updateWorkspacePermissionsSuccess({
                  permissions,
                });
              })
            );
        },
        onError: (_, httpResponse: HttpErrorResponse) => {
          if (httpResponse.status === 500) {
            this.appService.toastError(httpResponse, {
              label: 'errors.save_changes',
              message: 'errors.please_refresh',
            });
          } else {
            this.appService.errorManagement(httpResponse);
          }
          return ProjectActions.updateRolePermissionsError();
        },
      })
    );
  });

  constructor(
    private actions$: Actions,
    private projectApiService: ProjectApiService,
    private appService: AppService
  ) {}
}