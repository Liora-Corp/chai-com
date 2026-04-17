
import { type Request, type Response } from 'express'
import config from 'config'

export function retrieveAppConfiguration () {
  return (_req: Request, res: Response) => {
    res.json({ config: config.util.toObject() })
  }
}
