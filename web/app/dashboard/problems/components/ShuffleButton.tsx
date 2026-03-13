/**
 * Shuffle Button Component
 * 
 * Simple shuffle button that integrates with the pagination cache service
 * and provides consistent shuffle functionality across the problems page.
 */

import React from "react";
import { Button } from "@/shared/components/ui/button";
import { Shuffle, Dice5 } from "lucide-react";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";

interface ShuffleButtonProps {
  onShuffle?: () => void;
  fallbackShuffle?: () => void;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
  showLabel?: boolean;
  className?: string;
  disabled?: boolean;
}

export const ShuffleButton: React.FC<ShuffleButtonProps> = ({
  onShuffle,
  fallbackShuffle,
  variant = "default",
  size = "sm",
  showLabel = true,
  className = "",
  disabled = false
}) => {
  const { isShuffling, shuffleQuestions } = usePaginationCacheStore();

  const handleShuffle = async () => {
    if (disabled || isShuffling) return;

    try {
      console.log('🎲 ShuffleButton: Attempting to shuffle questions...');
      // Try using the cache service first
      const success = await shuffleQuestions();

      if (!success) {
        console.warn('⚠️ ShuffleButton: Cache-based shuffle failed, falling back to legacy shuffle');
        // Fall back to the provided fallback method
        if (fallbackShuffle) {
          fallbackShuffle();
        } else if (onShuffle) {
          // Call additional shuffle handler if provided
          onShuffle();
        }
      } else {
        console.log('✅ ShuffleButton: Questions shuffled successfully using cache service');
        if (onShuffle) {
          // Call additional shuffle handler if provided
          onShuffle();
        }
      }
    } catch (error) {
      console.error('❌ ShuffleButton: Shuffle failed:', error);

      // Use fallback if available
      if (fallbackShuffle) {
        fallbackShuffle();
      } else if (onShuffle) {
        onShuffle();
      }
    }
  };

  const isEffectivelyDisabled = disabled || isShuffling;

  return (
    <Button
      onClick={handleShuffle}
      disabled={isEffectivelyDisabled}
      variant={variant}
      size={size}
      className={`flex items-center gap-2 ${className}`}
      title="Shuffle the order of questions randomly"
      aria-label="Shuffle the order of questions randomly"
    >
      <Dice5
        size={16}
        className={isShuffling ? "animate-spin" : ""}
        aria-hidden="true"
      />
      {showLabel && (
        <span className="text-sm">
          {isShuffling ? "Shuffling..." : "Shuffle"}
        </span>
      )}
    </Button>
  );
};