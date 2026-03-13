"use client";

import { useState } from "react";
import { MessageSquare, X, Send, Loader2, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/shared/components/ui/button";
import { Textarea } from "@/shared/components/ui/textarea";
import { Label } from "@/shared/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/shared/components/ui/select";
import { usePathname } from "next/navigation";

export function FeedbackButton() {
    const [isOpen, setIsOpen] = useState(false);
    const [type, setType] = useState("suggestion");
    const [content, setContent] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const pathname = usePathname();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const res = await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    type,
                    content,
                    url: window.location.href,
                }),
            });

            if (res.ok) {
                setIsSuccess(true);
                setTimeout(() => {
                    setIsOpen(false);
                    setIsSuccess(false);
                    setContent("");
                }, 2000);
            }
        } catch (error) {
            console.error("Failed to submit feedback:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Floating Button */}
            <Button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 rounded-full h-12 w-12 shadow-2xl z-50 hover:scale-110 transition-transform bg-primary text-primary-foreground"
                size="icon"
            >
                <MessageSquare className="w-6 h-6" />
            </Button>

            {/* Modal Overlay */}
            <AnimatePresence>
                {isOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="bg-background border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden"
                        >
                            <div className="p-6 space-y-4">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-bold">Share your feedback</h2>
                                    <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                                        <X className="w-4 h-4" />
                                    </Button>
                                </div>

                                {isSuccess ? (
                                    <div className="py-8 flex flex-col items-center justify-center space-y-3 text-center">
                                        <CheckCircle2 className="w-12 h-12 text-green-500 animate-bounce" />
                                        <p className="font-medium">Thank you for helping us improve!</p>
                                        <p className="text-sm text-muted-foreground">Your feedback has been received.</p>
                                    </div>
                                ) : (
                                    <form onSubmit={handleSubmit} className="space-y-4">
                                        <div className="space-y-2">
                                            <Label>Feedback Type</Label>
                                            <Select value={type} onValueChange={setType}>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="suggestion">💡 Suggestion</SelectItem>
                                                    <SelectItem value="bug">🐛 Bug Report</SelectItem>
                                                    <SelectItem value="feature_request">🚀 Feature Request</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Your Message</Label>
                                            <Textarea
                                                placeholder="Tell us what's on your mind..."
                                                value={content}
                                                onChange={(e) => setContent(e.target.value)}
                                                required
                                                className="min-h-[120px] resize-none"
                                            />
                                        </div>

                                        <p className="text-[10px] text-muted-foreground italic">
                                            Submitting from: {pathname}
                                        </p>

                                        <Button type="submit" className="w-full gap-2" disabled={isLoading || !content.trim()}>
                                            {isLoading ? (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <Send className="w-4 h-4" />
                                            )}
                                            Submit Feedback
                                        </Button>
                                    </form>
                                )}
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </>
    );
}
