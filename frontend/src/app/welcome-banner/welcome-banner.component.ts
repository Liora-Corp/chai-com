/*
 * Copyright (c) 2014-2026 Bjoern Kimminich & the WowChai-Com contributors.
 * SPDX-License-Identifier: MIT
 */

import { Component, type OnInit, inject } from "@angular/core";
import { ConfigurationService } from "../Services/configuration.service";
import { MatDialogRef } from "@angular/material/dialog";
import { CookieService } from "ngy-cookie";
import { TranslateModule } from "@ngx-translate/core";

import { MatIconModule } from "@angular/material/icon";
import { MatTooltip } from "@angular/material/tooltip";
import { MatButtonModule } from "@angular/material/button";

@Component({
  selector: "app-welcome-banner",
  templateUrl: "welcome-banner.component.html",
  styleUrls: ["./welcome-banner.component.scss"],
  imports: [MatButtonModule, MatTooltip, MatIconModule, TranslateModule],
})
export class WelcomeBannerComponent implements OnInit {
  dialogRef = inject<MatDialogRef<WelcomeBannerComponent>>(MatDialogRef);
  private readonly configurationService = inject(ConfigurationService);
  private readonly cookieService = inject(CookieService);

  public title = "Welcome to WowChai-Com";
  public message =
    "<p><strong>WowChai-Com</strong> is a modern, full-featured e-commerce web application. Browse our product catalog, manage your account, and enjoy a seamless online shopping experience.</p><h1><a href='https://owasp-chai-com' target='_blank'>https://owasp-chai-com</a></h1>";
  public showHackingInstructor = true;
  public showDismissBtn = true;

  private readonly welcomeBannerStatusCookieKey = "welcomebanner_status";

  ngOnInit(): void {
    this.configurationService.getApplicationConfiguration().subscribe({
      next: (config) => {
        if (config?.application?.welcomeBanner) {
          this.title = config.application.welcomeBanner.title;
          this.message = config.application.welcomeBanner.message;
        }
        this.showHackingInstructor = config?.hackingInstructor?.isEnabled;
        // Don't allow to skip the tutorials when restrictToTutorialsFirst and showHackingInstructor are enabled
        if (
          this.showHackingInstructor &&
          config?.challenges?.restrictToTutorialsFirst
        ) {
          this.dialogRef.disableClose = true;
          this.showDismissBtn = false;
        }
      },
      error: (err) => {
        console.log(err);
      },
    });
  }

  startHackingInstructor() {
    this.closeWelcome();
    console.log('Starting instructions for challenge "Score Board"');
    import(/* webpackChunkName: "tutorial" */ "../../hacking-instructor").then(
      (module) => {
        module.startHackingInstructorFor("Score Board");
      },
    );
  }

  closeWelcome(): void {
    this.dialogRef.close();
    const expires = new Date();
    expires.setFullYear(expires.getFullYear() + 1);
    this.cookieService.put(this.welcomeBannerStatusCookieKey, "dismiss", {
      expires,
    });
  }
}
