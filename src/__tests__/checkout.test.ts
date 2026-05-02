import { getCheckoutItem } from '../routes/checkout'

// ── SQLi regression suite ─────────────────────────────────────────────────────
// Covers cc2 (PCI-DSS Req 6.3.2) and cc8 (OWASP A03:2021).
// Every payload listed here was confirmed exploitable against the pre-patch
// db.raw() implementation by the red-team agent on 2026-04-30.

describe('SQLi regression', () => {
  it.each([
    ["' OR 1=1--"],
    ['UNION SELECT * FROM users--'],
    ['\x00'],
  ])('blocks payload %s', async (payload) => {
    await expect(getCheckoutItem(payload)).rejects.toThrow()
  })
})
