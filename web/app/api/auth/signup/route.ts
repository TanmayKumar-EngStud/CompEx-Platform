
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import bcrypt from "bcryptjs";
import { sendOtpEmail } from "@/shared/lib/services/mail-service";

function generateOTP() {
    return Math.floor(100000 + Math.random() * 900000).toString();
}

export async function POST(req: NextRequest) {
    try {
        const { username, email, password } = await req.json();

        // 1. Validation
        if (!username || !email || !password) {
            return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
        }

        // 2. Check existence
        const existingUser = await prisma.users.findFirst({
            where: {
                OR: [
                    { email: email },
                    { username: username }
                ]
            }
        });

        if (existingUser) {
            if (existingUser.isverified) {
                return NextResponse.json({ error: "User already exists" }, { status: 409 });
            }
            // If user exists but is NOT verified, allow them to "re-signup" (update password/OTP)
            console.log(`Unverified user ${email} attempting re-signup. Updating...`);
        }

        // 3. Hash Password & Generate OTP
        const hashedPassword = await bcrypt.hash(password, 10);
        const otp = generateOTP();
        console.log("----------------------------------------------------------------");
        console.log(`🔐 SIGNUP OTP for ${email}: ${otp}`);
        console.log("----------------------------------------------------------------");

        // 4. Create or Update User
        const userData = {
            username,
            email,
            password: hashedPassword,
            otp,
            isverified: false
        };

        const user = await prisma.users.upsert({
            where: { email },
            update: userData,
            create: userData
        });

        // 5. Send OTP Email
        const emailSent = await sendOtpEmail(email, otp, 'signup');

        if (!emailSent) {
            console.error(`Failed to send signup OTP to ${email}`);
            // Note: We still return success as the user is created, 
            // but we might want to handle this better in production.
        }

        return NextResponse.json({
            message: existingUser ? "OTP resent. Please verify." : "User created successfully. OTP sent.",
            userId: user.userid
        });

    } catch (error) {
        console.error("Signup Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
