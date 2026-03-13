"use client";

import React, { useState, useEffect } from "react";
import { User, ChevronDown, LogOut, Settings } from "lucide-react";
import { UserAvatar } from "@/shared/components/feedback/UserAvatar";
import { AccountSettingsModal } from "./AccountSettingsModal";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

interface DBUser {
    userid: number;
    username: string;
    email: string;
    image_url?: string | null;
}

const UserSwitcher: React.FC = () => {
    const { userId, setUserId } = useAttemptsStore();
    const [users, setUsers] = useState<DBUser[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const router = useRouter();

    const handleLogout = async () => {
        try {
            const response = await fetch("/api/auth/logout", { method: "POST" });
            if (response.ok) {
                // Clear any relevant local state if necessary
                setUserId(0); // Reset local user state
                router.push("/"); // Redirect to landing page
            } else {
                console.error("Logout failed");
            }
        } catch (error) {
            console.error("Error during logout:", error);
        }
    };

    useEffect(() => {
        const initializeUser = async () => {
            try {
                // First, fetch the currently logged-in user from the session
                const meRes = await fetch("/api/auth/me");
                if (meRes.ok) {
                    const me = await meRes.json();
                    setUserId(me.userid);
                }

                // Then fetch all users for the list
                const usersRes = await fetch("/api/users");
                if (usersRes.ok) {
                    const data = await usersRes.json();
                    setUsers(data);
                }
            } catch (error) {
                console.error("Failed to initialize user:", error);
            }
        };

        initializeUser();
    }, [userId]);

    const refreshUser = async () => {
        try {
            const meRes = await fetch("/api/auth/me");
            if (meRes.ok) {
                const me = await meRes.json();
                setUsers(prev => prev.map(u => u.userid === me.userid ? me : u));
            }
        } catch (error) {
            console.error("Failed to refresh user:", error);
        }
    };

    const currentUser = users.find((u) => u.userid === userId);

    if (userId === 0) return null;

    return (
        <div
            className="relative"
            onMouseEnter={() => !isSettingsOpen && setIsOpen(true)}
            onMouseLeave={() => setIsOpen(false)}
        >
            <button
                onClick={() => currentUser?.username && router.push(`/u/${currentUser.username}`)}
                className="flex items-center p-1 px-2 rounded-full hover:bg-accent transition-all duration-200 border border-border bg-card shadow-sm group"
                aria-label="User profile"
            >
                <UserAvatar
                    username={currentUser?.username || 'default'}
                    image_url={currentUser?.image_url}
                    size="sm"
                />
                <ChevronDown size={14} className={clsx("ml-1.5 text-muted-foreground transition-transform duration-200", isOpen && "rotate-180")} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            transition={{ duration: 0.2 }}
                            className="absolute right-0 mt-2 w-64 bg-card border border-border rounded-xl shadow-xl z-50 overflow-hidden"
                        >
                            <div className="p-4 border-b border-border bg-muted/30">
                                <div className="flex items-center space-x-3">
                                    <UserAvatar
                                        username={currentUser?.username || 'default'}
                                        image_url={currentUser?.image_url}
                                        size="md"
                                    />
                                    <div className="flex flex-col min-w-0">
                                        <span className="text-sm font-bold text-foreground truncate">
                                            {currentUser?.username}
                                        </span>
                                        <span className="text-xs text-muted-foreground truncate">
                                            {currentUser?.email}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="p-2 border-t border-border bg-muted/20 space-y-1">
                                <button
                                    onClick={() => {
                                        if (currentUser) {
                                            router.push(`/u/${currentUser.username}`);
                                            setIsOpen(false);
                                        }
                                    }}
                                    className="w-full flex items-center space-x-2 px-3 py-2.5 rounded-lg text-sm text-foreground hover:bg-accent transition-all duration-200 group"
                                >
                                    <div className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                        <User size={14} />
                                    </div>
                                    <span className="font-medium">My Profile</span>
                                </button>
                                <button
                                    onClick={() => {
                                        setIsSettingsOpen(true);
                                        setIsOpen(false);
                                    }}
                                    className="w-full flex items-center space-x-2 px-3 py-2.5 rounded-lg text-sm text-foreground hover:bg-accent transition-all duration-200 group"
                                >
                                    <div className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                        <Settings size={14} />
                                    </div>
                                    <span className="font-medium">Account Settings</span>
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center space-x-2 px-3 py-2.5 rounded-lg text-sm text-red-500 hover:bg-red-500/10 transition-all duration-200 group"
                                >
                                    <div className="w-6 h-6 rounded-md bg-red-500/10 flex items-center justify-center text-red-500 group-hover:bg-red-500 group-hover:text-white transition-colors">
                                        <LogOut size={14} />
                                    </div>
                                    <span className="font-medium">Log Out</span>
                                </button>
                                <div className="pt-2 px-3">
                                    <div className="h-px bg-border/50 w-full mb-2" />
                                    <p className="text-[10px] text-muted-foreground text-center font-medium">
                                        Session resets on page reload
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>

            {currentUser && (
                <AccountSettingsModal
                    userId={userId}
                    currentUser={currentUser}
                    isOpen={isSettingsOpen}
                    onClose={() => setIsSettingsOpen(false)}
                    onUpdate={refreshUser}
                />
            )}
        </div>
    );
};

export default UserSwitcher;
