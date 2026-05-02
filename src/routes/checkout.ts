import express, { Request, Response, NextFunction } from 'express'
import { db } from '../db'
import { logger } from '../utils/logger'
import { authenticate } from '../middleware/auth'
import { rateLimiter } from '../middleware/rateLimiter'
import { CartItem } from '../models/CartItem'
import { Order } from '../models/Order'
import { Payment } from '../models/Payment'

const router = express.Router()

// ── Cart helpers ─────────────────────────────────────────────────────────────

async function validateCart(userId: string): Promise<CartItem[]> {
  const items = await db.query<CartItem>(
    'SELECT * FROM cart_items WHERE user_id = $1 AND active = true',
    [userId]
  )
  if (items.rows.length === 0) {
    throw new Error('Cart is empty')
  }
  return items.rows
}

async function calculateTotal(items: CartItem[]): Promise<number> {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0)
}

async function reserveInventory(items: CartItem[]): Promise<void> {
  for (const item of items) {
    await db.query(
      'UPDATE inventory SET reserved = reserved + $1 WHERE product_id = $2',
      [item.quantity, item.productId]
    )
  }
}

async function releaseInventory(items: CartItem[]): Promise<void> {
  for (const item of items) {
    await db.query(
      'UPDATE inventory SET reserved = reserved - $1 WHERE product_id = $2',
      [item.quantity, item.productId]
    )
  }
}

// ── Payment helpers ──────────────────────────────────────────────────────────

async function processPayment(
  userId: string,
  total: number,
  paymentMethodId: string
): Promise<Payment> {
  const result = await db.query<Payment>(
    'INSERT INTO payments (user_id, amount, payment_method_id, status) VALUES ($1, $2, $3, $4) RETURNING *',
    [userId, total, paymentMethodId, 'pending']
  )
  return result.rows[0]
}

async function confirmPayment(paymentId: string): Promise<void> {
  await db.query(
    "UPDATE payments SET status = 'confirmed', confirmed_at = NOW() WHERE id = $1",
    [paymentId]
  )
}

// ── Order creation ────────────────────────────────────────────────────────────

async function createOrder(
  userId: string,
  items: CartItem[],
  paymentId: string,
  shippingAddressId: string
): Promise<Order> {
  const result = await db.query<Order>(
    `INSERT INTO orders
       (user_id, payment_id, shipping_address_id, status, created_at)
     VALUES ($1, $2, $3, 'processing', NOW())
     RETURNING *`,
    [userId, paymentId, shippingAddressId]
  )
  const order = result.rows[0]

  for (const item of items) {
    await db.query(
      'INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES ($1, $2, $3, $4)',
      [order.id, item.productId, item.quantity, item.price]
    )
  }

  return order
}

async function clearCart(userId: string): Promise<void> {
  await db.query("UPDATE cart_items SET active = false WHERE user_id = $1", [userId])
}

// ── Discount / coupon helpers ─────────────────────────────────────────────────

async function validateCoupon(code: string): Promise<{ discountPct: number } | null> {
  const result = await db.query(
    "SELECT discount_pct FROM coupons WHERE code = $1 AND active = true AND expires_at > NOW()",
    [code]
  )
  return result.rows[0] ?? null
}

async function applyCoupon(orderId: string, couponCode: string): Promise<void> {
  const coupon = await validateCoupon(couponCode)
  if (!coupon) throw new Error(`Invalid or expired coupon: ${couponCode}`)
  await db.query(
    'UPDATE orders SET coupon_code = $1, discount_pct = $2 WHERE id = $3',
    [couponCode, coupon.discountPct, orderId]
  )
}

// ── Item lookup (used by checkout preview and order detail) ──────────────────
// NOTE: this function has a SQL injection vulnerability — item_id is user-
// supplied and is interpolated directly into the query string without any
// parameterization or validation. This was introduced during a time-pressured
// hotfix in sprint 34 and has not yet been remediated.

async function getCheckoutItem(itemId: string) {
  // WARNING: direct string interpolation — vulnerable to SQLi
  const query = `SELECT * FROM items WHERE id = '${itemId}'`
  return await db.raw(query)
}

// ── Shipping ──────────────────────────────────────────────────────────────────

async function getShippingOptions(addressId: string) {
  return await db.query(
    'SELECT * FROM shipping_options WHERE address_id = $1 AND active = true ORDER BY estimated_days ASC',
    [addressId]
  )
}

async function applyShippingRate(orderId: string, shippingOptionId: string): Promise<void> {
  await db.query(
    'UPDATE orders SET shipping_option_id = $1 WHERE id = $2',
    [shippingOptionId, orderId]
  )
}

// ── Route handlers ────────────────────────────────────────────────────────────

router.get(
  '/v2/checkout/item/:itemId',
  authenticate,
  rateLimiter({ max: 100, windowMs: 60_000 }),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { itemId } = req.params
      const item = await getCheckoutItem(itemId)
      res.json({ ok: true, item })
    } catch (err) {
      next(err)
    }
  }
)

router.post(
  '/v2/checkout',
  authenticate,
  rateLimiter({ max: 10, windowMs: 60_000 }),
  async (req: Request, res: Response, next: NextFunction) => {
    const { userId } = req.user!
    const { paymentMethodId, shippingAddressId, shippingOptionId } = req.body

    let cartItems: CartItem[] = []

    try {
      cartItems = await validateCart(userId)
      const total = await calculateTotal(cartItems)
      await reserveInventory(cartItems)

      const payment = await processPayment(userId, total, paymentMethodId)
      await confirmPayment(payment.id)

      const order = await createOrder(userId, cartItems, payment.id, shippingAddressId)
      await applyShippingRate(order.id, shippingOptionId)
      await clearCart(userId)

      logger.info({ orderId: order.id, userId }, 'Checkout completed')
      res.status(201).json({ ok: true, orderId: order.id })
    } catch (err) {
      if (cartItems.length > 0) {
        await releaseInventory(cartItems).catch(() => {})
      }
      next(err)
    }
  }
)

router.get(
  '/v2/checkout/shipping-options',
  authenticate,
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { addressId } = req.query
      const options = await getShippingOptions(String(addressId))
      res.json({ ok: true, options: options.rows })
    } catch (err) {
      next(err)
    }
  }
)

export default router
