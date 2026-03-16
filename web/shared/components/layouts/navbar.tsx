"use client";

import React, { useEffect, useState } from "react";
import Header from "@/shared/components/layouts/header";
import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useStreak } from "@/shared/contexts/StreakContext";
import ThemeToggle from "@/shared/components/interactive/theme-toggle";
import UserSwitcher from "@/shared/components/interactive/UserSwitcher";
import ProblemsStreak from "@/shared/components/interactive/ProblemsStreak";
import { ButtonS, ButtonP } from "@/shared/components/ui/button";
import { Sfont } from "@/shared/lib/configs/fonts";
import { Hexagon } from "lucide-react";

const BrandLogo = () => (
    <div className="flex items-center gap-2.5 group select-none">
        <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-all duration-300">
            <Hexagon className="w-5 h-5 text-primary fill-primary/20 group-hover:scale-110 transition-transform duration-300" strokeWidth={2.5} />
        </div>
        <Sfont style={1} className="text-2xl font-bold tracking-tight text-foreground">
            Comp<span className="text-primary">Ex</span>
        </Sfont>
    </div>
);

const Navbar: React.FC = () => {
    const pathname = usePathname();
    const { userId, setUserId } = useAttemptsStore();
    const { streakData, loading: streakLoading } = useStreak();
    // If we already have a userId from Zustand, we consider it initialized immediately
    const [isInitialized, setIsInitialized] = useState(() => userId !== 0);


    // Sync auth state on mount
    useEffect(() => {
        const checkAuth = async () => {
            try {
                // Ensure auth is never cached so changing login states are always reflected
                const res = await fetch("/api/auth/me", { 
                    cache: 'no-store',
                    headers: { 'Cache-Control': 'no-cache' }
                });
                if (res.ok) {
                    const data = await res.json();
                    setUserId(data.userid);
                } else {
                    setUserId(0);
                }
            } catch (error) {
                console.error("Auth check failed", error);
                setUserId(0);
            } finally {
                setIsInitialized(true);
            }
        };
        checkAuth();
    }, [setUserId]);

    const navLinks = [
        { name: "Explore", href: "/dashboard/explore" },
        { name: "Problems", href: "/dashboard/problems" },
        { name: "Mock", href: "/dashboard/mock" },
        { name: "Learn", href: "/learn" },
    ];

    const renderLeft = () => {
        const logo = (
            <Link href="/" key="logo-left" className="no-underline">
                <BrandLogo />
            </Link>
        );

        if (userId === 0) return [
            logo,
            <Link
                key="learn"
                href="/learn"
                className={clsx(
                    "text-sm font-medium transition-colors hover:text-primary",
                    pathname.startsWith("/learn") ? "text-foreground font-semibold" : "text-muted-foreground"
                )}
            >
                Learn
            </Link>,
        ];
        return navLinks.map((link, index) => {
            const isActive = link.href === "/learn"
                ? pathname.startsWith("/learn")
                : pathname === link.href;
            return (
                <Link
                    key={index}
                    href={link.href}
                    data-tour={`nav-${link.name.toLowerCase()}`}
                    className={clsx(
                        "text-sm font-medium transition-colors hover:text-primary",
                        isActive ? "text-foreground font-semibold" : "text-muted-foreground"
                    )}
                >
                    {link.name}
                </Link>
            );
        });
    };

    const renderCenter = () => {
        const logo = (
            <Link href="/" className="no-underline">
                <BrandLogo />
            </Link>
        );

        if (userId === 0) return []; // Logo moves to the right for unauthenticated
        return [logo];
    };

    const renderRight = () => {
        const logo = (
            <div key="logo-right">
                <BrandLogo />
            </div>
        );

        if (userId === 0) {
            return [
                <Link href="/login" key="login" passHref>
                    <ButtonS className="h-9 px-6 text-sm">Log in</ButtonS>
                </Link>,
                <Link href="/signup?force=true" key="signup" passHref>
                    <ButtonP className="h-9 px-6 text-sm">Sign up</ButtonP>
                </Link>,
                <ThemeToggle key="theme" />,
            ];
        }

        return [
            <div key="auth-right" className="flex gap-4 items-center">
                <div data-tour="streak-counter">
                    <ProblemsStreak streak={streakLoading ? 0 : streakData.currentstreak} />
                </div>
                <div data-tour="user-menu">
                    <UserSwitcher />
                </div>
            </div>,
        ];
    };

    // Show unauthenticated layout immediately while auth check is in progress
    // This prevents the navbar from being invisible during API compilation/cold start
    if (!isInitialized) {
        return (
            <Header
                leftItems={[
                    <Link href="/" key="logo-left" className="no-underline">
                        <BrandLogo />
                    </Link>,
                    <Link
                        key="learn"
                        href="/learn"
                        className="text-sm font-medium transition-colors hover:text-primary text-muted-foreground"
                    >
                        Learn
                    </Link>,
                ]}
                centerItems={[]}
                rightItems={[
                    <Link href="/login" key="login" passHref>
                        <ButtonS className="h-9 px-6 text-sm">Log in</ButtonS>
                    </Link>,
                    <Link href="/signup?force=true" key="signup" passHref>
                        <ButtonP className="h-9 px-6 text-sm">Sign up</ButtonP>
                    </Link>,
                    <ThemeToggle key="theme" />,
                ]}
                gap={4}
            />
        );
    }

    return (
        <Header
            leftItems={renderLeft()}
            centerItems={renderCenter()}
            rightItems={renderRight()}
            gap={userId === 0 ? 4 : 8}
        />
    );
};

export default Navbar;
