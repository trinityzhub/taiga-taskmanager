/**
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Copyright (c) 2021-present Kaleidos Ventures SL
 */

import { Directive, Input, OnDestroy } from '@angular/core';
import { RestoreFocusService } from './restore-focus.service';

@Directive({
  selector: '[tgRestoreFocus]',
  standalone: true,
})
export class RestoreFocusDirective implements OnDestroy {
  @Input('tgRestoreFocus')
  public id!: string;

  @Input('tgRestoreFocusActive')
  public active = true;

  constructor(private focusService: RestoreFocusService) {}

  public ngOnDestroy(): void {
    if (this.active) {
      this.focusService.focusWhenAvailable(this.id);
    }
  }
}
