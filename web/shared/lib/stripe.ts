// Stripe Subscription Integration for Compex
// Simple, ethical, transparent pricing

import Stripe from 'stripe'

// Initialize Stripe (use env variables)
// Initialize Stripe (use env variables, fall back to dummy for build)
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || 'sk_test_placeholder_for_build', {
  apiVersion: '2023-10-16',
})

// Pricing Tiers
export const SUBSCRIPTION_PLANS = {
  free: {
    id: 'free',
    name: 'Free',
    price: 0,
    priceId: null,
    features: [
      '10 questions/day',
      'Basic analytics',
      'Community support',
    ],
  },
  pro: {
    id: 'pro',
    name: 'Pro',
    price: 9.99,
    priceId: process.env.STRIPE_PRO_PRICE_ID || 'price_pro_monthly',
    interval: 'month' as const,
    features: [
      'Unlimited questions',
      'Detailed analytics',
      'Mock papers',
      'Priority support',
      'Export data',
    ],
  },
  team: {
    id: 'team',
    name: 'Team',
    price: 29.99,
    priceId: process.env.STRIPE_TEAM_PRICE_ID || 'price_team_monthly',
    interval: 'month' as const,
    features: [
      'Everything in Pro',
      'Up to 5 team members',
      'Shared progress',
      'Admin dashboard',
      'API access',
    ],
  },
}

// Create Checkout Session
export async function createCheckoutSession({
  userId,
  priceId,
  successUrl,
  cancelUrl,
}: {
  userId: string
  priceId: string
  successUrl: string
  cancelUrl: string
}) {
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    metadata: {
      userId,
    },
    success_url: successUrl,
    cancel_url: cancelUrl,
    allow_promotion_codes: true,
    billing_address_collection: 'auto',
  })

  return session
}

// Create Customer Portal Session (manage subscriptions)
export async function createPortalSession({
  customerId,
  returnUrl,
}: {
  customerId: string
  returnUrl: string
}) {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  })

  return session
}

// Verify Webhook Signature
export function verifyWebhookSignature(
  payload: string | Buffer,
  signature: string
) {
  try {
    return stripe.webhooks.constructEvent(
      payload,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET || ''
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err)
    throw err
  }
}

// Handle Subscription Events
export async function handleSubscriptionEvent(event: Stripe.Event) {
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      // Update user to Pro in database
      await updateUserSubscription(session.metadata?.userId, 'pro')
      break
    }
    case 'customer.subscription.created': {
      const subscription = event.data.object as Stripe.Subscription
      // Update user subscription
      await updateUserSubscription(
        subscription.metadata?.userId,
        'pro'
      )
      break
    }
    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription
      // Downgrade to free
      await updateUserSubscription(
        subscription.metadata?.userId,
        'free'
      )
      break
    }
    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice
      // Notify user of payment failure
      await sendPaymentFailedNotification(invoice.customer as string)
      break
    }
  }
}

// Database helpers (implement these)
async function updateUserSubscription(userId: string | undefined, plan: string) {
  if (!userId) return
  // Update user in database
  // await prisma.users.update(...)
  console.log(`User ${userId} updated to ${plan}`)
}

async function sendPaymentFailedNotification(customerId: string) {
  // Send email/notification
  console.log(`Payment failed for customer ${customerId}`)
}

// Get subscription status
export async function getSubscriptionStatus(customerId: string) {
  try {
    const subscriptions = await stripe.subscriptions.list({
      customer: customerId,
      status: 'active',
      limit: 1,
    })

    if (subscriptions.data.length === 0) {
      return { active: false, plan: 'free' }
    }

    const subscription = subscriptions.data[0]
    const priceId = subscription.items.data[0].price.id

    const plan =
      priceId === SUBSCRIPTION_PLANS.team.priceId
        ? 'team'
        : priceId === SUBSCRIPTION_PLANS.pro.priceId
          ? 'pro'
          : 'free'

    return {
      active: true,
      plan,
      currentPeriodEnd: subscription.current_period_end * 1000,
    }
  } catch (error) {
    console.error('Error fetching subscription:', error)
    return { active: false, plan: 'free' }
  }
}

// Cancel subscription
export async function cancelSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  })
}

// Resume subscription
export async function resumeSubscription(subscriptionId: string) {
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: false,
  })
}
