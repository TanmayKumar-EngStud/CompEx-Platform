"use client";

import React, { useState, useEffect } from 'react';
import { Star, ThumbsUp, ThumbsDown, X, Sparkles, Gift } from 'lucide-react';
import { useAttemptsStore } from "@/shared/stores/problems/attempts";

interface QuestionFeedbackModalProps {
    questionId: number;
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (rating: number, comment: string) => void;
}

export default function QuestionFeedbackModal({
    questionId,
    isOpen,
    onClose,
    onSubmit
}: QuestionFeedbackModalProps) {
    const [rating, setRating] = useState(0);
    const [hoveredRating, setHoveredRating] = useState(0);
    const [comment, setComment] = useState('');
    const [isHelpful, setIsHelpful] = useState<boolean | null>(null);
    const [submitted, setSubmitted] = useState(false);
    const [reward, setReward] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { userId } = useAttemptsStore();

    const ratingLabels = {
        1: 'Very Poor',
        2: 'Poor',
        3: 'Below Average',
        4: 'Fair',
        5: 'Average',
        6: 'Good',
        7: 'Very Good',
        8: 'Excellent',
        9: 'Outstanding',
        10: 'Perfect'
    };

    const handleSubmit = async () => {
        if (rating === 0) return;

        setIsLoading(true);
        try {
            const res = await fetch('/api/feedback/question', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    questionId,
                    userId,
                    rating,
                    comment,
                    isHelpful
                })
            });

            const data = await res.json();

            if (data.reward) {
                setReward(data.reward);
            }

            setSubmitted(true);
            onSubmit(rating, comment);
        } catch (error) {
            console.error('Error submitting feedback:', error);
            setSubmitted(true); // Still show submitted state
        } finally {
            setIsLoading(false);
        }
    };

    const handleClose = () => {
        setRating(0);
        setComment('');
        setIsHelpful(null);
        setSubmitted(false);
        setReward(null);
        onClose();
    };

    if (!isOpen) return null;

    // Show reward animation
    if (reward) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in zoom-in duration-300">
                    <div className="p-8 text-center">
                        <div className="w-20 h-20 mx-auto mb-4 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center animate-bounce">
                            <Gift className="w-10 h-10 text-amber-600" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">You Earned a Badge!</h3>
                        <div className="text-4xl mb-2">{reward.collectibleIcon}</div>
                        <p className="text-lg font-semibold text-primary">{reward.collectibleName}</p>
                        <p className="text-sm text-muted-foreground mt-2">{reward.description}</p>
                    </div>
                    <div className="bg-muted/50 p-4 flex justify-center">
                        <button
                            onClick={handleClose}
                            className="px-6 py-2 bg-primary text-primary-foreground rounded-xl font-bold hover:bg-primary/90"
                        >
                            Awesome!
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Show thank you screen
    if (submitted) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in zoom-in duration-300">
                    <div className="p-8 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                            <Sparkles className="w-8 h-8 text-green-600" />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Thanks for your feedback!</h3>
                        <p className="text-muted-foreground">Your input helps improve Compex for everyone.</p>
                    </div>
                    <div className="bg-muted/50 p-4 flex justify-center">
                        <button
                            onClick={handleClose}
                            className="px-6 py-2 bg-primary text-primary-foreground rounded-xl font-bold hover:bg-primary/90"
                        >
                            Continue
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in zoom-in duration-200">
                {/* Header */}
                <div className="p-4 border-b border-border flex items-center justify-between">
                    <h3 className="font-bold text-lg">Rate This Question</h3>
                    <button
                        onClick={handleClose}
                        className="p-1 hover:bg-muted rounded-lg transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* Star Rating */}
                    <div className="text-center mb-6">
                        <p className="text-sm text-muted-foreground mb-3">How would you rate this question?</p>
                        <div className="flex justify-center gap-2">
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                                <button
                                    key={star}
                                    onClick={() => setRating(star)}
                                    onMouseEnter={() => setHoveredRating(star)}
                                    onMouseLeave={() => setHoveredRating(0)}
                                    className="p-1 transition-transform hover:scale-110"
                                >
                                    <Star
                                        size={28}
                                        className={`${star <= (hoveredRating || rating)
                                                ? 'fill-amber-400 text-amber-400'
                                                : 'text-muted-foreground/40'
                                            }`}
                                    />
                                </button>
                            ))}
                        </div>
                        {rating > 0 && (
                            <p className="mt-2 text-sm font-medium text-amber-600 dark:text-amber-400">
                                {ratingLabels[rating as keyof typeof ratingLabels]}
                            </p>
                        )}
                    </div>

                    {/* Thumbs Up/Down */}
                    <div className="mb-6">
                        <p className="text-sm text-muted-foreground mb-3 text-center">Was this question helpful?</p>
                        <div className="flex justify-center gap-4">
                            <button
                                onClick={() => setIsHelpful(true)}
                                className={`p-3 rounded-xl border transition-all ${isHelpful === true
                                        ? 'bg-green-50 border-green-200 text-green-600 dark:bg-green-900/20 dark:border-green-800'
                                        : 'border-border hover:bg-muted'
                                    }`}
                            >
                                <ThumbsUp size={24} />
                            </button>
                            <button
                                onClick={() => setIsHelpful(false)}
                                className={`p-3 rounded-xl border transition-all ${isHelpful === false
                                        ? 'bg-red-50 border-red-200 text-red-600 dark:bg-red-900/20 dark:border-red-800'
                                        : 'border-border hover:bg-muted'
                                    }`}
                            >
                                <ThumbsDown size={24} />
                            </button>
                        </div>
                    </div>

                    {/* Optional Comment */}
                    <div className="mb-4">
                        <label className="text-sm text-muted-foreground block mb-2">
                            Any additional comments? (optional)
                        </label>
                        <textarea
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            placeholder="The question was too hard, had an error, etc..."
                            className="w-full p-3 border border-border rounded-xl bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/20"
                            rows={3}
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 bg-muted/50 border-t border-border flex gap-3 justify-end">
                    <button
                        onClick={handleClose}
                        className="px-4 py-2 text-muted-foreground hover:text-foreground font-medium transition-colors"
                    >
                        Skip
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={rating === 0 || isLoading}
                        className="px-6 py-2 bg-primary text-primary-foreground rounded-xl font-bold hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Submitting...
                            </>
                        ) : (
                            'Submit Feedback'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
