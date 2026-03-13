"use client";

import React from 'react';

interface UserAvatarProps {
    username: string;
    image_url?: string | null;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({ username, image_url, size = 'md', className = '' }) => {
    const [imgError, setImgError] = React.useState(false);
    const initials = username.slice(0, 2).toUpperCase();

    React.useEffect(() => {
        setImgError(false);
    }, [image_url]);

    const getAvatarColor = (name: string) => {
        const colors = [
            'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500',
            'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500',
            'bg-teal-500', 'bg-cyan-500'
        ];
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    };

    const avatarColor = getAvatarColor(username);

    const sizeClasses = {
        sm: 'h-8 w-8 text-xs',
        md: 'h-10 w-10 text-sm',
        lg: 'h-16 w-16 text-xl',
        xl: 'h-24 w-24 text-3xl'
    };

    return (
        <div className={`${sizeClasses[size]} rounded-full overflow-hidden border-2 border-border relative ${avatarColor} flex items-center justify-center text-white font-bold shadow-inner ${className}`}>
            {image_url && !imgError ? (
                <img
                    src={image_url}
                    alt={username}
                    className="h-full w-full object-cover"
                    onError={() => setImgError(true)}
                />
            ) : (
                initials
            )}
        </div>
    );
};
