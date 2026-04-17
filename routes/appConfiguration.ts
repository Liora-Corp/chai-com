/*
 * Copyright (c) 2014-2026 Bjoern Kimminich & the WowChai-Com contributors.
 * SPDX-License-Identifier: MIT
 */

import { type Request, type Response } from 'express'
import config from 'config'

export function retrieveAppConfiguration () {
  return (_req: Request, res: Response) => {
    res.json({ config: config.util.toObject() })
  }
}