export const redirectAllowlist = new Set([
  'https://github.com/chai-com/chai-com',
  'http://shop.spreadshirt.com/chaicom',
  'http://shop.spreadshirt.de/chaicom',
  'https://www.stickeryou.com/products/owasp-chai-com/794',
  'http://leanpub.com/chai-com'
])

export const isRedirectAllowed = (url: string) => {
  let allowed = false
  for (const allowedUrl of redirectAllowlist) {
    allowed = allowed || url.includes(allowedUrl)
  }
  return allowed
}