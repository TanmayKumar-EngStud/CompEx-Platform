/**
 * Shuffle Controls Component
 * 
 * Advanced shuffle controls with strategy selection, preview functionality,
 * and integration with the shuffle service for intelligent question ordering.
 */

import React, { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { Switch } from "@/shared/components/ui/switch";
import { Badge } from "@/shared/components/feedback/badge";
import { Shuffle, Settings, Eye, RotateCcw, Zap } from "lucide-react";
import { ShuffleService, type ShuffleStrategy } from "../../services/shuffle.service";

interface ShuffleControlsProps {
  onShuffle: (strategy: ShuffleStrategy) => void;
  onPreviewShuffle?: (strategy: ShuffleStrategy) => void;
  onResetOrder?: () => void;
  isShuffling?: boolean;
  questionCount?: number;
  currentStrategy?: ShuffleStrategy;
  showAdvancedControls?: boolean;
  disabled?: boolean;
  className?: string;
}

const STRATEGY_LABELS: Record<ShuffleStrategy, string> = {
  'random': 'Random',
  'performance-weighted': 'Performance-based',
  'category-balanced': 'Category-balanced',
  'difficulty-progressive': 'Difficulty Progressive',
  'spaced-repetition': 'Spaced Repetition',
  'smart': 'Smart Shuffle'
};

const STRATEGY_DESCRIPTIONS: Record<ShuffleStrategy, string> = {
  'random': 'Completely random question order',
  'performance-weighted': 'Prioritizes questions you struggle with',
  'category-balanced': 'Balances questions across categories',
  'difficulty-progressive': 'Gradually increases difficulty',
  'spaced-repetition': 'Based on optimal review timing',
  'smart': 'Automatically chooses the best strategy'
};

export const ShuffleControls: React.FC<ShuffleControlsProps> = ({
  onShuffle,
  onPreviewShuffle,
  onResetOrder,
  isShuffling = false,
  questionCount = 0,
  currentStrategy = 'random',
  showAdvancedControls = false,
  disabled = false,
  className = ""
}) => {
  const [selectedStrategy, setSelectedStrategy] = useState<ShuffleStrategy>(currentStrategy);
  const [showSettings, setShowSettings] = useState(false);
  const [enablePreview, setEnablePreview] = useState(false);
  const [shuffleService] = useState(() => new ShuffleService({
    defaultStrategy: 'smart',
    enablePerformanceWeights: true,
    enableCategoryBalancing: true,
    enableDifficultyProgression: true,
    enableSpacedRepetition: true,
    logShuffleEvents: true
  }));

  const handleShuffle = () => {
    if (!disabled && !isShuffling) {
      onShuffle(selectedStrategy);
    }
  };

  const handlePreview = () => {
    if (onPreviewShuffle && !disabled && !isShuffling) {
      onPreviewShuffle(selectedStrategy);
    }
  };

  const handleResetOrder = () => {
    if (onResetOrder && !disabled && !isShuffling) {
      onResetOrder();
    }
  };

  const getStrategyIcon = (strategy: ShuffleStrategy) => {
    switch (strategy) {
      case 'smart':
        return <Zap size={16} />;
      case 'performance-weighted':
        return <span className="text-xs font-bold">📊</span>;
      case 'category-balanced':
        return <span className="text-xs font-bold">🔄</span>;
      case 'difficulty-progressive':
        return <span className="text-xs font-bold">📈</span>;
      case 'spaced-repetition':
        return <span className="text-xs font-bold">⏰</span>;
      default:
        return <Shuffle size={16} />;
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Basic Shuffle Button */}
      {!showAdvancedControls && (
        <Button
          onClick={handleShuffle}
          disabled={disabled || isShuffling}
          variant="outline"
          size="sm"
          className="flex items-center gap-2"
        >
          <Shuffle 
            size={16} 
            className={isShuffling ? "animate-spin" : ""} 
          />
          {isShuffling ? "Shuffling..." : "Shuffle"}
        </Button>
      )}

      {/* Advanced Controls */}
      {showAdvancedControls && (
        <>
          {/* Strategy Selection */}
          <Select
            value={selectedStrategy}
            onValueChange={(value: ShuffleStrategy) => setSelectedStrategy(value)}
            disabled={disabled || isShuffling}
          >
            <SelectTrigger className="w-48">
              <div className="flex items-center gap-2">
                {getStrategyIcon(selectedStrategy)}
                <SelectValue />
              </div>
            </SelectTrigger>
            <SelectContent>
              {Object.entries(STRATEGY_LABELS).map(([strategy, label]) => (
                <SelectItem key={strategy} value={strategy}>
                  <div className="flex items-center gap-2">
                    {getStrategyIcon(strategy as ShuffleStrategy)}
                    <div>
                      <div className="font-medium">{label}</div>
                      <div className="text-xs text-muted-foreground">
                        {STRATEGY_DESCRIPTIONS[strategy as ShuffleStrategy]}
                      </div>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            {/* Preview Button */}
            {enablePreview && onPreviewShuffle && (
              <Button
                onClick={handlePreview}
                disabled={disabled || isShuffling}
                variant="ghost"
                size="sm"
                title="Preview shuffle result"
              >
                <Eye size={16} />
              </Button>
            )}

            {/* Main Shuffle Button */}
            <Button
              onClick={handleShuffle}
              disabled={disabled || isShuffling}
              variant="default"
              size="sm"
              className="flex items-center gap-2"
            >
              <Shuffle 
                size={16} 
                className={isShuffling ? "animate-spin" : ""} 
              />
              {isShuffling ? "Shuffling..." : "Shuffle"}
            </Button>

            {/* Reset Button */}
            {onResetOrder && (
              <Button
                onClick={handleResetOrder}
                disabled={disabled || isShuffling}
                variant="ghost"
                size="sm"
                title="Reset to original order"
              >
                <RotateCcw size={16} />
              </Button>
            )}

            {/* Settings Popover */}
            <Popover open={showSettings} onOpenChange={setShowSettings}>
              <PopoverTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={disabled}
                  title="Shuffle settings"
                >
                  <Settings size={16} />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80" align="end">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Shuffle Settings</h4>
                    <p className="text-sm text-muted-foreground">
                      Configure how questions are shuffled
                    </p>
                  </div>

                  <div className="space-y-3">
                    {/* Preview Toggle */}
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium">Enable Preview</div>
                        <div className="text-xs text-muted-foreground">
                          Show preview button to see shuffle result
                        </div>
                      </div>
                      <Switch
                        checked={enablePreview}
                        onCheckedChange={setEnablePreview}
                        disabled={!onPreviewShuffle}
                      />
                    </div>

                    {/* Current Strategy Info */}
                    <div>
                      <div className="text-sm font-medium mb-1">Current Strategy</div>
                      <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                        {getStrategyIcon(selectedStrategy)}
                        {STRATEGY_LABELS[selectedStrategy]}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {STRATEGY_DESCRIPTIONS[selectedStrategy]}
                      </div>
                    </div>

                    {/* Question Count */}
                    {questionCount > 0 && (
                      <div>
                        <div className="text-sm font-medium">Questions to Shuffle</div>
                        <div className="text-sm text-muted-foreground">
                          {questionCount} questions
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          </div>
        </>
      )}

      {/* Status Badge */}
      {isShuffling && (
        <Badge variant="secondary" className="animate-pulse">
          Shuffling...
        </Badge>
      )}
    </div>
  );
};