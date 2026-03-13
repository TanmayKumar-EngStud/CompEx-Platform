"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/shared/components/ui/card";
import { AlertCircle, CheckCircle2, Loader2, ArrowLeft, Eye, EyeOff, Wand2, Home } from "lucide-react";
import Link from "next/link";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import {
    InputOTP,
    InputOTPGroup,
    InputOTPSlot
} from "@/shared/components/ui/input-otp";
import { isDev } from "@/shared/lib/utils/env";

type LoginMode = "login" | "forgot-request" | "forgot-reset";

const GoogleIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
    </svg>
)

const AppleIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="currentColor">
        <path d="M17.05 20.28c-.98.95-2.05.8-3.08.3-1.09-.5-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.48-2.73-2.92-3.11-6.73-.25-9.52 1.48-1.43 3.05-1.57 4.19-.51 1.08 1.02 2.12 1.06 3.27.02 1.34-1.21 2.92-1.04 4.5.34 1.11.96 1.83 2 2.29 2.54-1.98.53-3.08 1.11-3.66 2.33-.53 1.09.28 3.12 1.38 4.67-.84 1.16-1.52 1.62-2.34 2.82V20.28zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
    </svg>
)

function LoginContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const verified = searchParams.get("verified");

    // Visibility state
    const [showPassword, setShowPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // Global Store
    const { setUserId } = useAttemptsStore();

    // UI State
    const [mode, setMode] = useState<LoginMode>("login");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | React.ReactNode>("");
    const [success, setSuccess] = useState("");

    // Shared Form State
    const [formData, setFormData] = useState({
        identifier: "",
        password: ""
    });

    // Forgot Password State
    const [otp, setOtp] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const handleAutoFill = () => {
        setFormData({
            identifier: "tanmay44a@gmail.com",
            password: "tk@CompEx!"
        });
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        try {
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await res.json();

            if (!res.ok) {
                if (data.isVerified === false) {
                    throw new Error("Account not verified. Please verify your email.");
                }
                throw new Error(data.error || "Login failed");
            }

            // 1. Update Global State
            if (data.user?.id) {
                setUserId(data.user.id);
            }

            // 2. Redirect to Explore Page
            router.push("/dashboard/explore");
            router.refresh();

        } catch (err: any) {
            if (err.message === "Account not verified. Please verify your email.") {
                setError(
                    <span>
                        Account not verified.{" "}
                        <Link href="/signup" className="underline font-bold hover:text-primary transition-colors">
                            Verify your email here.
                        </Link>
                    </span>
                );
            } else {
                setError(err.message);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleRequestOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        try {
            const res = await fetch("/api/auth/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: formData.identifier })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Failed to send OTP");

            setMode("forgot-reset");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (newPassword !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setIsLoading(true);

        try {
            const res = await fetch("/api/auth/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: formData.identifier, otp, newPassword })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Reset failed");

            setSuccess("Password reset successful! You can now log in.");
            setMode("login");
            setOtp("");
            setNewPassword("");
            setConfirmPassword("");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // --- RENDER MODES ---

    if (mode === "forgot-request") {
        return (
            <Card className="w-full border-border/60 shadow-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold">Forgot Password</CardTitle>
                    <CardDescription>Enter your Email or Userid to receive a reset code.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleRequestOtp} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="identifier">Email or Userid</Label>
                            <Input
                                id="identifier"
                                type="text"
                                placeholder="Email or Username"
                                required
                                value={formData.identifier}
                                onChange={(e) => setFormData({ ...formData, identifier: e.target.value })}
                            />
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 text-sm text-red-500 bg-red-50 p-2 rounded">
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </div>
                        )}

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Send Reset Code"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter>
                    <Button variant="ghost" className="w-full" onClick={() => setMode("login")}>
                        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Login
                    </Button>
                </CardFooter>
            </Card>
        );
    }

    if (mode === "forgot-reset") {
        return (
            <Card className="w-full border-border/60 shadow-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold">Reset Password</CardTitle>
                    <CardDescription>Enter the code sent to {formData.identifier}</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleResetPassword} className="space-y-4">
                        <div className="space-y-2 flex flex-col items-center">
                            <Label className="self-start">Verification Code</Label>
                            <InputOTP maxLength={6} value={otp} onChange={(val: string) => setOtp(val)}>
                                <InputOTPGroup>
                                    <InputOTPSlot index={0} />
                                    <InputOTPSlot index={1} />
                                    <InputOTPSlot index={2} />
                                    <InputOTPSlot index={3} />
                                    <InputOTPSlot index={4} />
                                    <InputOTPSlot index={5} />
                                </InputOTPGroup>
                            </InputOTP>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="newPassword">New Password</Label>
                            <div className="relative">
                                <Input
                                    id="newPassword"
                                    type={showNewPassword ? "text" : "password"}
                                    required
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowNewPassword(!showNewPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                >
                                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Confirm New Password</Label>
                            <div className="relative">
                                <Input
                                    id="confirmPassword"
                                    type={showConfirmPassword ? "text" : "password"}
                                    required
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                >
                                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 text-sm text-red-500 bg-red-50 p-2 rounded">
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </div>
                        )}

                        <Button type="submit" className="w-full" disabled={isLoading || otp.length < 6}>
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Reset Password"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter>
                    <Button variant="ghost" className="w-full" onClick={() => setMode("forgot-request")}>
                        <ArrowLeft className="w-4 h-4 mr-2" /> Change Email or Userid
                    </Button>
                </CardFooter>
            </Card>
        );
    }

    // --- LOGIN RENDER (Default) ---
    return (
        <div className="relative w-full">
            <div className="absolute -top-12 left-0 right-0 flex justify-between items-center">
                <Link href="/">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 text-xs font-medium text-muted-foreground hover:text-foreground"
                    >
                        <Home className="w-3 h-3" />
                        Back to Home
                    </Button>
                </Link>

                {isDev && (
                    <Button
                        variant="outline"
                        size="sm"
                        className="gap-2 border-primary/20 hover:border-primary/50 text-xs font-bold"
                        onClick={handleAutoFill}
                        type="button"
                        disabled={isLoading}
                    >
                        <Wand2 className="w-3 h-3" />
                        AUTO
                    </Button>
                )}
            </div>

            <Card className="w-full border-border/60 shadow-lg">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold">Welcome back</CardTitle>
                    <CardDescription>Enter your Email or Userid to sign in to your account</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="mb-6">
                        <Button variant="outline" className="w-full" type="button" onClick={() => { window.location.href = "/api/auth/google"; }}>
                            <GoogleIcon className="mr-2 h-4 w-4" /> Continue with Google
                        </Button>
                    </div>
                    <div className="relative mb-6">
                        <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t border-muted-foreground/20" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                        </div>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-4">

                        {verified && !success && (
                            <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded border border-green-200">
                                <CheckCircle2 className="w-4 h-4" />
                                Account verified successfully! Please log in.
                            </div>
                        )}

                        {success && (
                            <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded border border-green-200">
                                <CheckCircle2 className="w-4 h-4" />
                                {success}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="identifier">Email or Userid</Label>
                            <Input
                                id="identifier"
                                type="text"
                                placeholder="Email or Username"
                                required
                                value={formData.identifier}
                                onChange={(e) => setFormData({ ...formData, identifier: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <Button
                                    type="button"
                                    variant="link"
                                    className="px-0 h-auto text-sm font-medium"
                                    onClick={() => setMode("forgot-request")}
                                >
                                    Forgot password?
                                </Button>
                            </div>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    required
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="flex items-center gap-2 text-sm text-red-500 bg-red-50 p-2 rounded">
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </div>
                        )}

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Log in"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="justify-center text-sm text-muted-foreground">
                    Don&apos;t have an account?
                    <Link href="/signup" className="ml-1 text-primary hover:underline font-medium">Sign up</Link>
                </CardFooter>
            </Card>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <LoginContent />
        </Suspense>
    );
}
