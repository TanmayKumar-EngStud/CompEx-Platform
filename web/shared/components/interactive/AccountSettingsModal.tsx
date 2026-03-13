"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactDOM from "react-dom";
import { X, Upload, User, Mail, Check, AlertCircle, Loader2, Trash2, AlertTriangle, Sun, Moon, Settings2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { UserAvatar } from "@/shared/components/feedback/UserAvatar";
import { ButtonP, ButtonS } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import Cropper from 'react-easy-crop';
import { getCroppedImg } from "@/shared/lib/utils/image-crop";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { examSectionService } from "@/features/exam-management/services/exam-section-service";
import { useTheme } from "next-themes";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/shared/components/ui/select";
import { useTutorialStore } from "@/shared/stores/tutorial-store";
import { useRouter, usePathname } from "next/navigation";

interface AccountSettingsModalProps {
    userId: number;
    currentUser: {
        username: string;
        email: string;
        image_url?: string | null;
    };
    isOpen: boolean;
    onClose: () => void;
    onUpdate: () => void;
    isFirstLogin?: boolean;
}

export const AccountSettingsModal: React.FC<AccountSettingsModalProps> = ({
    userId,
    currentUser,
    isOpen,
    onClose,
    onUpdate,
    isFirstLogin = false,
}) => {
    const router = useRouter();
    const pathname = usePathname();
    const [username, setUsername] = useState(currentUser.username);
    const [email] = useState(currentUser.email); // Email usually read-only in simple settings
    const [isUploading, setIsUploading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [isDeletingLoading, setIsDeletingLoading] = useState(false);
    const [deleteConfirmUsername, setDeleteConfirmUsername] = useState('');
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Preferences state
    const { examName, setExamName, setSectionName, setSectionIndex, setCategoryIndex } = usePaginationStore();
    const { resolvedTheme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    // First-login onboarding: track if user has explicitly selected an exam
    const [hasSelectedExam, setHasSelectedExam] = useState(false);
    // Animate the toggle demo on first login
    const [demoAnimating, setDemoAnimating] = useState(false);
    const [demoExam, setDemoExam] = useState(examName);

    useEffect(() => {
        setMounted(true);
    }, []);

    // On first login, play a demo animation that slides between GRE and GMAT
    useEffect(() => {
        if (!isFirstLogin || !mounted || hasSelectedExam) return;

        setDemoAnimating(true);
        const steps = [
            { exam: "GRE", delay: 600 },
            { exam: "GMAT", delay: 1400 },
            { exam: "GRE", delay: 2200 },
            { exam: "GMAT", delay: 3000 },
            { exam: "GRE", delay: 3800 },
        ];

        const timers = steps.map(({ exam, delay }) =>
            setTimeout(() => setDemoExam(exam), delay)
        );

        const endTimer = setTimeout(() => {
            setDemoAnimating(false);
        }, 4400);

        return () => {
            timers.forEach(clearTimeout);
            clearTimeout(endTimer);
        };
    }, [isFirstLogin, mounted, hasSelectedExam]);

    // Cropping state
    const [imageSrc, setImageSrc] = useState<string | null>(null);
    const [crop, setCrop] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const [croppedAreaPixels, setCroppedAreaPixels] = useState<any>(null);
    const [showCropper, setShowCropper] = useState(false);

    const onCropComplete = (croppedArea: any, croppedAreaPixels: any) => {
        setCroppedAreaPixels(croppedAreaPixels);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.addEventListener('load', () => {
                setImageSrc(reader.result as string);
                setShowCropper(true);
            });
            reader.readAsDataURL(file);
        }
    };

    const handleUploadCroppedImage = async () => {
        if (!imageSrc || !croppedAreaPixels) return;

        setIsUploading(true);
        setMessage(null);
        setShowCropper(false);

        try {
            const croppedImageBlob = await getCroppedImg(imageSrc, croppedAreaPixels);
            const file = new File([croppedImageBlob], "avatar.jpg", { type: "image/jpeg" });

            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("/api/users/upload-pfp", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Upload failed");
            }

            setMessage({ type: 'success', text: "Profile picture updated!" });
            onUpdate();
        } catch (error: any) {
            console.error("PFP Upload error:", error);
            setMessage({ type: 'error', text: error.message || "Failed to upload image." });
        } finally {
            setIsUploading(false);
            setImageSrc(null);
        }
    };

    const handleSaveProfile = async () => {
        // On first login with no username change, just close the modal
        if (isFirstLogin && username === currentUser.username) {
            onClose();
            return;
        }

        setIsSaving(true);
        setMessage(null);

        try {
            const response = await fetch("/api/users/profile", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username }),
            });

            if (response.ok) {
                setMessage({ type: 'success', text: "Profile updated successfully!" });
                onUpdate();
                // Close after a brief delay to show success message
                setTimeout(() => {
                    onClose();
                }, 800);
            } else {
                const data = await response.json();
                setMessage({ type: 'error', text: data.error || "Failed to update profile." });
            }
        } catch (error) {
            setMessage({ type: 'error', text: "Something went wrong." });
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (deleteConfirmUsername !== currentUser.username) return;

        setIsDeletingLoading(true);
        try {
            const res = await fetch(`/api/users/${currentUser.username}`, {
                method: 'DELETE',
            });

            if (res.ok) {
                // Clear all compex-related localStorage so returning user gets fresh state
                const keysToRemove: string[] = [];
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && (key.startsWith("compex-") || key === "app-build-info")) {
                        keysToRemove.push(key);
                    }
                }
                keysToRemove.forEach((key) => localStorage.removeItem(key));

                // Logout and redirect
                await fetch('/api/auth/logout', { method: 'POST' });
                window.location.href = '/';
            } else {
                const data = await res.json();
                setMessage({ type: 'error', text: data.error || 'Failed to delete account' });
            }
        } catch (error) {
            console.error('Error deleting account:', error);
            setMessage({ type: 'error', text: 'An error occurred while deleting your account' });
        } finally {
            setIsDeletingLoading(false);
        }
    };

    const handleReplayTutorial = (tourId: string) => {
        const { resetTour, startTour } = useTutorialStore.getState();

        // Close the settings modal
        onClose();

        // Navigate to the relevant page first, then start tour
        const routeMap: Record<string, string> = {
            welcome: "/dashboard/explore",
            explore: "/dashboard/explore",
            problems: "/dashboard/problems",
            mock: "/dashboard/mock",
            profile: `/u/${currentUser.username}`,
        };

        const targetRoute = routeMap[tourId];
        if (targetRoute && pathname !== targetRoute) {
            router.push(targetRoute);
        }

        // Small delay for navigation + modal close animation
        setTimeout(() => {
            resetTour(tourId);
            startTour(tourId);
        }, 600);
    };

    // Prevent body scroll when modal is open
    React.useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
            // Also ensure pointer events are restored
            document.body.style.pointerEvents = 'auto';
        }
        return () => {
            document.body.style.overflow = 'unset';
            document.body.style.pointerEvents = 'auto';
        };
    }, [isOpen]);

    if (!mounted) return null;

    // Use a portal to render the modal at the document root, escaping any parent stacking contexts
    return ReactDOM.createPortal(
        <AnimatePresence mode="wait">
            {isOpen && (
                <>
                    {/* Backdrop overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        key="backdrop"
                        className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-md"
                        onClick={isFirstLogin && !hasSelectedExam ? undefined : onClose}
                    />

                    {/* Modal container */}
                    <div className="fixed inset-0 z-[101] flex items-center justify-center p-4 pointer-events-none overflow-y-auto">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            key="modal-content"
                            className="relative w-full max-w-4xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden my-8 pointer-events-auto"
                        >    {/* Header */}
                            <div className="flex items-center justify-between p-6 border-b border-border bg-muted/30">
                                <div className="flex items-center space-x-2">
                                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                                        <User size={20} />
                                    </div>
                                    <h2 className="text-xl font-bold text-foreground">Account Settings</h2>
                                </div>
                                {(!isFirstLogin || hasSelectedExam) && (
                                    <button
                                        onClick={onClose}
                                        className="p-2 hover:bg-accent rounded-full text-muted-foreground transition-colors"
                                    >
                                        <X size={20} />
                                    </button>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-border">
                                {/* Left Sidebar: Identity & Danger Zone */}
                                <div className="md:col-span-5 lg:col-span-4 p-6 bg-muted/5 flex flex-col space-y-6">
                                    {/* Avatar Section */}
                                    <div className="flex flex-col items-center space-y-4">
                                        <div className="relative group">
                                            <UserAvatar
                                                username={currentUser.username}
                                                image_url={currentUser.image_url}
                                                size="xl"
                                                className="w-32 h-32 text-2xl"
                                            />
                                            <button
                                                onClick={() => fileInputRef.current?.click()}
                                                disabled={isUploading}
                                                className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 rounded-full transition-opacity cursor-pointer"
                                                aria-label="Change profile picture"
                                            >
                                                {isUploading ? (
                                                    <Loader2 className="w-8 h-8 text-white animate-spin" />
                                                ) : (
                                                    <Upload className="w-8 h-8 text-white" />
                                                )}
                                            </button>
                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept="image/*"
                                                className="hidden"
                                                onChange={handleFileSelect}
                                            />
                                        </div>

                                        <div className="text-center">
                                            <p className="font-semibold text-foreground">{currentUser.username}</p>
                                            <p className="text-xs text-muted-foreground">Joined February 2026</p>
                                        </div>
                                    </div>

                                    <div className="flex-1" /> {/* Spacer */}

                                    {/* Danger Zone - Sidebar */}
                                    <div className="pt-6 border-t border-border/50">
                                        {!isDeleting ? (
                                            <button
                                                onClick={() => setIsDeleting(true)}
                                                className="group flex items-center space-x-2 text-xs font-medium text-muted-foreground hover:text-red-600 transition-colors py-2"
                                            >
                                                <div className="p-1.5 rounded-md group-hover:bg-red-500/10 transition-colors">
                                                    <Trash2 className="w-4 h-4" />
                                                </div>
                                                <span>Delete Account</span>
                                            </button>
                                        ) : (
                                            <div className="space-y-3 animate-in fade-in slide-in-from-left-2 duration-200">
                                                <div className="bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                                                    <p className="text-xs font-bold text-red-600 mb-1">Are you sure?</p>
                                                    <p className="text-[10px] text-red-600/80 leading-tight">
                                                        Permanent data loss.
                                                    </p>
                                                </div>
                                                <Input
                                                    value={deleteConfirmUsername}
                                                    onChange={(e) => setDeleteConfirmUsername(e.target.value)}
                                                    placeholder={`Type ${currentUser.username}`}
                                                    className="h-8 text-xs border-red-500/30 bg-background"
                                                    autoFocus
                                                />
                                                <div className="flex gap-2">
                                                    <ButtonS
                                                        onClick={() => setIsDeleting(false)}
                                                        className="flex-1 h-8 text-xs"
                                                    >
                                                        Cancel
                                                    </ButtonS>
                                                    <ButtonP
                                                        onClick={handleDeleteAccount}
                                                        disabled={deleteConfirmUsername !== currentUser.username || isDeletingLoading}
                                                        className="flex-1 h-8 text-xs bg-red-500 hover:bg-red-600 border-none"
                                                    >
                                                        {isDeletingLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : "Confirm"}
                                                    </ButtonP>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Right Content: Forms & Preferences */}
                                <div className="md:col-span-7 lg:col-span-8 p-6 md:p-8 space-y-8">
                                    {isFirstLogin && (
                                        <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 animate-in fade-in slide-in-from-top-2">
                                            <h3 className="text-lg font-bold text-primary mb-1">Welcome to CompEx!</h3>
                                            <AnimatePresence mode="wait">
                                                {!hasSelectedExam ? (
                                                    <motion.p
                                                        key="select-prompt"
                                                        initial={{ opacity: 0 }}
                                                        animate={{ opacity: 1 }}
                                                        exit={{ opacity: 0 }}
                                                        className="text-sm text-muted-foreground"
                                                    >
                                                        First, select which exam you&apos;re preparing for below.
                                                    </motion.p>
                                                ) : (
                                                    <motion.p
                                                        key="selected-confirm"
                                                        initial={{ opacity: 0, y: 4 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        className="text-sm text-muted-foreground"
                                                    >
                                                        Nice, so you want to prepare for <span className="font-bold text-primary">{examName}</span>. Now let&apos;s get started!
                                                    </motion.p>
                                                )}
                                            </AnimatePresence>
                                        </div>
                                    )}

                                    <div className="space-y-6">
                                        <div className="grid grid-cols-1 gap-6">
                                            <div className="space-y-2">
                                                <Label htmlFor="username">Username</Label>
                                                <div className="relative">
                                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                                                        <User size={16} />
                                                    </div>
                                                    <Input
                                                        id="username"
                                                        value={username}
                                                        onChange={(e) => setUsername(e.target.value)}
                                                        className="pl-10 h-10 bg-background"
                                                        placeholder="Your username"
                                                    />
                                                </div>
                                            </div>
                                            <div className="space-y-2">
                                                <Label htmlFor="email">Email Address</Label>
                                                <div className="relative">
                                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                                                        <Mail size={16} />
                                                    </div>
                                                    <Input
                                                        id="email"
                                                        value={email}
                                                        disabled
                                                        className="pl-10 h-10 bg-muted/50 cursor-not-allowed text-muted-foreground"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Preferences Grid */}
                                    <div className="space-y-4">
                                        <h4 className="text-sm font-bold text-foreground flex items-center gap-2 pb-2 border-b border-border">
                                            <Settings2 className="w-4 h-4 text-primary" />
                                            Preferences
                                        </h4>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                            {/* Exam Type - Animated Toggle */}
                                            <div className={`p-3 rounded-xl border bg-card transition-all duration-500 ${
                                                isFirstLogin && !hasSelectedExam
                                                    ? 'border-primary/50 shadow-[0_0_20px_rgba(var(--primary-rgb,59,130,246),0.15)] ring-1 ring-primary/20'
                                                    : 'border-border hover:bg-muted/50'
                                            }`}>
                                                {isFirstLogin && !hasSelectedExam && (
                                                    <motion.p
                                                        initial={{ opacity: 0, y: -4 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        className="text-xs font-semibold text-primary mb-2 flex items-center gap-1.5"
                                                    >
                                                        <span className="relative flex h-2 w-2">
                                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
                                                        </span>
                                                        Select your target exam to continue
                                                    </motion.p>
                                                )}
                                                <Label className="text-xs font-medium text-muted-foreground mb-2 block">Exam Type</Label>
                                                <div className="relative flex bg-muted rounded-lg p-1">
                                                    {/* Animated sliding background */}
                                                    <motion.div
                                                        className="absolute top-1 bottom-1 rounded-md shadow-sm"
                                                        animate={{
                                                            left: (isFirstLogin && !hasSelectedExam && demoAnimating ? demoExam : examName) === "GRE" ? "4px" : "50%",
                                                            width: "calc(50% - 4px)",
                                                        }}
                                                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                                                        style={{
                                                            background: "var(--background)",
                                                            boxShadow: `0 0 12px rgba(var(--primary-rgb, 59, 130, 246), ${
                                                                isFirstLogin && !hasSelectedExam ? '0.4' : '0.1'
                                                            })`,
                                                        }}
                                                    />
                                                    {["GRE", "GMAT"].map((exam) => {
                                                        const displayExam = isFirstLogin && !hasSelectedExam && demoAnimating ? demoExam : examName;
                                                        const isActive = displayExam === exam;
                                                        return (
                                                            <button
                                                                key={exam}
                                                                onClick={() => {
                                                                    setExamName(exam);
                                                                    const defaultSection = examSectionService.getDefaultSectionForExam(exam);
                                                                    setSectionName(defaultSection);
                                                                    setSectionIndex(0);
                                                                    setCategoryIndex(0);
                                                                    if (isFirstLogin) setHasSelectedExam(true);
                                                                }}
                                                                className={`relative z-10 flex-1 py-1.5 text-xs font-bold rounded-md transition-colors duration-200 ${
                                                                    isActive
                                                                        ? 'text-primary'
                                                                        : 'text-muted-foreground hover:text-foreground'
                                                                }`}
                                                            >
                                                                <motion.span
                                                                    animate={isActive && isFirstLogin && !hasSelectedExam ? {
                                                                        textShadow: [
                                                                            "0 0 4px rgba(var(--primary-rgb, 59, 130, 246), 0)",
                                                                            "0 0 8px rgba(var(--primary-rgb, 59, 130, 246), 0.6)",
                                                                            "0 0 4px rgba(var(--primary-rgb, 59, 130, 246), 0)",
                                                                        ],
                                                                    } : {}}
                                                                    transition={isActive && isFirstLogin && !hasSelectedExam ? {
                                                                        duration: 1.5,
                                                                        repeat: Infinity,
                                                                        ease: "easeInOut",
                                                                    } : {}}
                                                                >
                                                                    {exam}
                                                                </motion.span>
                                                            </button>
                                                        );
                                                    })}
                                                </div>
                                            </div>

                                            {/* Theme */}
                                            <div className="p-3 rounded-xl border border-border bg-card hover:bg-muted/50 transition-colors">
                                                <Label className="text-xs font-medium text-muted-foreground mb-2 block">Theme</Label>
                                                {mounted && (
                                                    <div className="flex bg-muted rounded-lg p-1">
                                                        <button
                                                            onClick={() => setTheme('light')}
                                                            className={`flex-1 py-1.5 flex items-center justify-center gap-1.5 text-xs font-medium rounded-md transition-all ${resolvedTheme === 'light'
                                                                ? 'bg-background text-primary shadow-sm'
                                                                : 'text-muted-foreground hover:text-foreground'
                                                                }`}
                                                        >
                                                            <Sun size={12} /> Light
                                                        </button>
                                                        <button
                                                            onClick={() => setTheme('dark')}
                                                            className={`flex-1 py-1.5 flex items-center justify-center gap-1.5 text-xs font-medium rounded-md transition-all ${resolvedTheme === 'dark'
                                                                ? 'bg-background text-primary shadow-sm'
                                                                : 'text-muted-foreground hover:text-foreground'
                                                                }`}
                                                        >
                                                            <Moon size={12} /> Dark
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Replay Tutorials Section */}
                                    <div className="space-y-3 pt-4 border-t border-border">
                                        <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                                            Replay Tutorials
                                        </h4>
                                        <p className="text-xs text-muted-foreground">
                                            Re-watch the guided tutorial for any page
                                        </p>
                                        <Select onValueChange={(value) => handleReplayTutorial(value)}>
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder="Select a page tutorial..." />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="welcome">Welcome Tour (Navbar Overview)</SelectItem>
                                                <SelectItem value="explore">Explore Page</SelectItem>
                                                <SelectItem value="problems">Problems Page</SelectItem>
                                                <SelectItem value="mock">Mock Exams Page</SelectItem>
                                                <SelectItem value="profile">Profile & Analytics</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    {/* Status Message */}
                                    <AnimatePresence>
                                        {message && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: 'auto' }}
                                                exit={{ opacity: 0, height: 0 }}
                                                className={`flex items-center space-x-2 p-3 rounded-lg text-sm font-medium ${message.type === 'success'
                                                    ? 'bg-green-500/10 text-green-600 border border-green-500/20'
                                                    : 'bg-red-500/10 text-red-600 border border-red-500/20'
                                                    }`}
                                            >
                                                {message.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
                                                <span>{message.text}</span>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>



                            {/* Re-adding Cropper Overlay here (it uses fixed positioning so location in DOM doesn't matter much) */}
                            <AnimatePresence>
                                {showCropper && imageSrc && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="fixed inset-0 z-[110] bg-black/90 flex flex-col items-center justify-center p-4 lg:p-8"
                                    >
                                        <div className="relative w-full max-w-2xl aspect-square bg-card rounded-2xl overflow-hidden shadow-2xl">
                                            <Cropper
                                                image={imageSrc}
                                                crop={crop}
                                                zoom={zoom}
                                                aspect={1}
                                                cropShape="round"
                                                showGrid={false}
                                                onCropChange={setCrop}
                                                onCropComplete={onCropComplete}
                                                onZoomChange={setZoom}
                                            />
                                        </div>

                                        <div className="mt-8 w-full max-w-md space-y-6">
                                            <div className="flex flex-col space-y-2">
                                                <label className="text-white/60 text-xs font-medium uppercase tracking-wider text-center">Zoom Level</label>
                                                <input
                                                    type="range"
                                                    value={zoom}
                                                    min={1}
                                                    max={3}
                                                    step={0.1}
                                                    aria-labelledby="Zoom"
                                                    onChange={(e) => setZoom(Number(e.target.value))}
                                                    className="w-full h-1.5 bg-white/20 rounded-lg appearance-none cursor-pointer accent-primary"
                                                />
                                            </div>

                                            <div className="flex gap-4">
                                                <ButtonS
                                                    onClick={() => {
                                                        setShowCropper(false);
                                                        setImageSrc(null);
                                                    }}
                                                    className="flex-1 bg-white/10 hover:bg-white/20 text-white border-none h-12"
                                                >
                                                    Cancel
                                                </ButtonS>
                                                <ButtonP
                                                    onClick={handleUploadCroppedImage}
                                                    className="flex-1 h-12 shadow-xl shadow-primary/20"
                                                >
                                                    Apply Crop
                                                </ButtonP>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Actions */}
                            <div className="p-6 border-t border-border bg-muted/30 flex justify-end space-x-3">
                                {(!isFirstLogin || hasSelectedExam) && (
                                    <ButtonS onClick={onClose} className="bg-transparent hover:bg-accent text-muted-foreground border-none shadow-none">Cancel</ButtonS>
                                )}
                                {isFirstLogin && hasSelectedExam ? (
                                    <motion.div
                                        animate={{ scale: [1, 1.06, 1] }}
                                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                                    >
                                        <ButtonP
                                            onClick={handleSaveProfile}
                                            disabled={isSaving}
                                            className="px-8 ring-2 ring-primary/50 ring-offset-2 ring-offset-background"
                                        >
                                            {isSaving ? (
                                                <span className="flex items-center gap-2">
                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                    Saving...
                                                </span>
                                            ) : "Get Started →"}
                                        </ButtonP>
                                    </motion.div>
                                ) : (
                                    <ButtonP
                                        onClick={isFirstLogin && !hasSelectedExam ? undefined : handleSaveProfile}
                                        disabled={isSaving || (isFirstLogin ? !hasSelectedExam : username === currentUser.username)}
                                        className="px-8"
                                    >
                                        {isSaving ? (
                                            <span className="flex items-center gap-2">
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Saving...
                                            </span>
                                        ) : (isFirstLogin ? "Select an Exam Above" : "Save Changes")}
                                    </ButtonP>
                                )}
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence >,
        document.body
    );
};
