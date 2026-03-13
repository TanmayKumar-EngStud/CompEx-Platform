
"use client";

import React, { useState } from 'react';
import { Settings, Trash2, X, AlertTriangle, Loader2 } from 'lucide-react';
import { ButtonP, ButtonS } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/shared/components/ui/card';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

import { AccountSettingsModal } from '@/shared/components/interactive/AccountSettingsModal';

interface EditProfileButtonProps {
    user: {
        userid: number;
        username: string;
        email: string;
        image_url?: string | null;
    };
}

export function EditProfileButton({ user }: EditProfileButtonProps) {
    const [isOpen, setIsOpen] = useState(false);
    const router = useRouter();

    return (
        <div className="w-full mt-4">
            <ButtonS
                onClick={() => setIsOpen(true)}
                className="w-full flex items-center justify-center gap-2 h-10 border-primary/20 hover:bg-primary/5 transition-all text-sm"
            >
                <Settings className="w-4 h-4" />
                Edit Profile
            </ButtonS>

            <AccountSettingsModal
                userId={user.userid}
                currentUser={user}
                isOpen={isOpen}
                onClose={() => setIsOpen(false)}
                onUpdate={() => router.refresh()}
            />
        </div>
    );
}
