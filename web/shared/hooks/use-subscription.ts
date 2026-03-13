import { useState, useEffect } from 'react';

// Mock subscription hook - will be replaced with actual API call when Stripe is integrated
export function useSubscription() {
  const [tier, setTier] = useState<'free' | 'pro' | 'team'>('free');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API call to check user subscription
    // For now, defaulting to free tier
    const fetchSubscriptionStatus = async () => {
      try {
        // const response = await fetch('/api/subscription/status');
        // const data = await response.json();
        // setTier(data.tier);

        // Temporarily defaulting to pro to remove barriers for users
        // setTier('free'); 
        setTier('pro');
      } catch (error) {
        console.error('Error fetching subscription status:', error);
        setTier('pro'); // Fallback to pro instead of free
      } finally {
        setIsLoading(false);
      }
    };

    fetchSubscriptionStatus();
  }, []);

  return {
    tier,
    isLoading,
    isPro: tier === 'pro' || tier === 'team',
    isFree: tier === 'free',
    isTeam: tier === 'team'
  };
}
