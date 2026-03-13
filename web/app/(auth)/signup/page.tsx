"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/shared/components/ui/card";
import { AlertCircle, CheckCircle2, Loader2, ArrowRight, Eye, EyeOff, Wand2 } from "lucide-react";
import Link from "next/link";
import {
    InputOTP,
    InputOTPGroup,
    InputOTPSlot
} from "@/shared/components/ui/input-otp";
import { isDev } from "@/shared/lib/utils/env";
import { Home } from "lucide-react";

const GoogleIcon = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
    </svg>
);

export default function SignupPage() {
    const router = useRouter();
    const [step, setStep] = useState<"register" | "verify">("register");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    // Visibility state
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: ""
    });
    const [otp, setOtp] = useState("");

    const handleAutoFill = () => {
        const randomId = Math.floor(Math.random() * 10000);
        const randomUser = `user_${randomId}`;
        const randomEmail = `test_${randomId}@example.com`;
        const pass = "Password123!";

        setFormData({
            username: randomUser,
            email: randomEmail,
            password: pass,
            confirmPassword: pass
        });
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setIsLoading(true);

        try {
            const res = await fetch("/api/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Registration failed");
            }

            // Success -> Move to OTP step
            setStep("verify");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        try {
            const res = await fetch("/api/auth/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: formData.email,
                    otp
                })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Verification failed");
            }

            // Success -> Redirect to dashboard
            router.push("/dashboard/explore");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    if (step === "verify") {
        return (
            <Card className="w-full border-border/60 shadow-lg">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">Verify your Email</CardTitle>
                    <CardDescription>
                        We&apos;ve sent a 6-digit code to <span className="font-medium text-foreground">{formData.email}</span>.
                        <br />(Check the server console for the code in this MVP)
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleVerify} className="space-y-6 flex flex-col items-center">
                        <div className="flex justify-center w-full">
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

                        {error && (
                            <div className="flex items-center gap-2 text-sm text-red-500 bg-red-50 p-2 rounded w-full">
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </div>
                        )}

                        <Button type="submit" className="w-full" disabled={isLoading || otp.length < 6}>
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Verify Account"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        );
    }

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
                    >
                        <Wand2 className="w-3 h-3" />
                        AUTO
                    </Button>
                )}
            </div>

            <Card className="w-full border-border/60 shadow-lg">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
                    <CardDescription>Enter your email below to create your account</CardDescription>
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
                            <span className="bg-background px-2 text-muted-foreground">Or continue with email</span>
                        </div>
                    </div>
                    <form onSubmit={handleRegister} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                placeholder="johndoe"
                                required
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="m@example.com"
                                required
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
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
                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <div className="relative">
                                <Input
                                    id="confirmPassword"
                                    type={showConfirmPassword ? "text" : "password"}
                                    required
                                    value={formData.confirmPassword}
                                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
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

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : "Create account"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="justify-center text-sm text-muted-foreground">
                    Already have an account?
                    <Link href="/login" className="ml-1 text-primary hover:underline font-medium">Log in</Link>
                </CardFooter>
            </Card>
        </div>
    );
}
