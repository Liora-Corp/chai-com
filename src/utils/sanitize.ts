// Utility helpers for input sanitization

export function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

export function sanitizeInput(value: string): string {
  // Strip SQL metacharacters as defense-in-depth
  return value.replace(/['";\\--]/g, '')
}

