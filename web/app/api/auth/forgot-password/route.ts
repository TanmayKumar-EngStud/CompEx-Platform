
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import { sendOtpEmail } from "@/shared/lib/services/mail-service";

export async function POST(req: NextRequest) {
    try {
        const { email } = await req.json();

        if (!email) {
            return NextResponse.json({ error: "Email is required" }, { status: 400 });
        }

        const user = await prisma.users.findUnique({
            where: { email }
        });

        if (!user) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        // Generate 6-digit OTP
        const otp = Math.floor(100000 + Math.random() * 900000).toString();
        console.log("----------------------------------------------------------------");
        console.log(`🔐 RESET PASSWORD OTP for ${email}: ${otp}`);
        console.log("----------------------------------------------------------------");

        await prisma.users.update({
            where: { email },
            data: { otp }
        });

        // Send OTP Email
        const emailSent = await sendOtpEmail(email, otp, 'reset');

        if (!emailSent) {
            console.error(`Failed to send password reset OTP to ${email}`);
        }

        return NextResponse.json({ message: "OTP sent to your email" });

    } catch (error) {
        console.error("Forgot Password Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
