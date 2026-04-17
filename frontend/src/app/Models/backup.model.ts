/*
 * Copyright (c) 2014-2026 Bjoern Kimminich & the WowChai-Com contributors.
 * SPDX-License-Identifier: MIT
 */

export interface Backup {
  version: number;
  continueCode?: string;
  continueCodeFindIt?: string;
  continueCodeFixIt?: string;
  language?: string;
  banners?: { welcomeBannerStatus?: string; cookieConsentStatus?: string };
}
