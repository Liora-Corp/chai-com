/*
 * Copyright (c) 2014-2026 Bjoern Kimminich & the OWASP Chai-Com contributors.
 * SPDX-License-Identifier: MIT
 */

export interface Hint {
  id: number
  ChallengeId: number
  text: string
  order: number
  unlocked?: boolean
}
