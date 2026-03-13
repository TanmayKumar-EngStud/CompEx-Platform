// API Route: Create Subscription Checkout
// POST /api/subscriptions/checkout

import { NextRequest, NextResponse } from 'next/server'
import { createCheckoutSession, SUBSCRIPTION_PLANS } from '@/lib/stripe'
import { jose } from '@/lib/jwt'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    // Get user from token
    const token = request.cookies.get('token')?.value
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      )
    }

    const payload = await jose.jwtVerify(token)
    const userId = payload.userId as number

    // Get user from database
    const user = await prisma.users.findUnique({
      where: { userid: userId },
      select: { email: true, stripeCustomerId: true },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Parse request body
    const body = await request.json()
    const { planId } = body

    // Validate plan
    const plan = SUBSCRIPTION_PLANS[planId as keyof typeof SUBSCRIPTION_PLANS]
    if (!plan || plan.price === 0) {
      return NextResponse.json(
        { error: 'Invalid plan' },
        { status: 400 }
      )
    }

    // Create Stripe customer if doesn't exist
    let customerId = user.stripeCustomerId
    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: { userId: String(userId) },
      })
      customerId = customer.id

      // Save to database
      await prisma.users.update({
        where: { userid: userId },
        data: { stripeCustomerId: customerId },
      })
    }

    // Create checkout session
    const origin = request.headers.get('origin') || 'http://localhost:3000'
    const session = await createCheckoutSession({
      userId: String(userId),
      priceId: plan.priceId!,
      successUrl: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancelUrl: `${origin}/pricing`,
    })

    return NextResponse.json({
      success: true,
      url: session.url,
      plan: {
        id: plan.id,
        name: plan.name,
        price: plan.price,
      },
    })
  } catch (error) {
    console.error('Checkout error:', error)
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    )
  }
}

import Stripe from 'stripe'

// Initialize Stripe (lazy load to avoid issues)
function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY || '', {
    apiVersion: '2023-10-16',
  })
}

const stripe = {
  customers: {
    create: async (data: any) => ({ id: 'cus_test' }),
  },
}
