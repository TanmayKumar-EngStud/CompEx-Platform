import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'localhost',
    port: parseInt(process.env.SMTP_PORT || '587'),
    secure: process.env.SMTP_SECURE === 'true', // true for 465, false for other ports
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
    },
});

const APP_NAME = 'CompEx';
const SENDER_EMAIL = '"CompEx" <no-reply@compex.live>';

/**
 * Sends an OTP email with a premium HTML template.
 */
export async function sendOtpEmail(email: string, otp: string, type: 'signup' | 'reset') {
    const subject = type === 'signup'
        ? `Welcome to ${APP_NAME}! Your Verification Code`
        : `Reset Your ${APP_NAME} Password`;

    const title = type === 'signup' ? 'Welcome to CompEx!' : 'Password Reset Request';
    const description = type === 'signup'
        ? 'Thank you for joining us. Please use the following code to verify your account.'
        : 'We received a request to reset your password. Use the code below to proceed.';

    const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${subject}</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8fafc;
                color: #1e293b;
            }
            .container {
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
            .header {
                background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
                padding: 40px 20px;
                text-align: center;
                color: #ffffff;
            }
            .header h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: -0.025em;
            }
            .content {
                padding: 40px;
                text-align: center;
            }
            .content p {
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
                margin-bottom: 32px;
            }
            .otp-container {
                background: #f1f5f9;
                padding: 24px;
                border-radius: 12px;
                display: inline-block;
                margin-bottom: 32px;
            }
            .otp-code {
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 36px;
                font-weight: 700;
                letter-spacing: 0.25em;
                color: #2563eb;
                margin: 0;
            }
            .footer {
                padding: 24px;
                text-align: center;
                font-size: 14px;
                color: #64748b;
                border-top: 1px solid #f1f5f9;
            }
            .footer a {
                color: #3b82f6;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>${title}</h1>
            </div>
            <div class="content">
                <p>${description}</p>
                <div class="otp-container">
                    <p class="otp-code">${otp}</p>
                </div>
                <p style="font-size: 14px; color: #94a3b8;">This code will expire in 10 minutes. If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; ${new Date().getFullYear()} CompEx. All rights reserved.</p>
                <p>Support: <a href="mailto:support@compex.live">support@compex.live</a></p>
            </div>
        </div>
    </body>
    </html>
    `;

    try {
        await transporter.sendMail({
            from: SENDER_EMAIL,
            to: email,
            subject: subject,
            html: html,
        });
        console.log(`Email sent successfully to ${email}`);
        return true;
    } catch (error) {
        console.error('Error sending email:', error);
        return false;
    }
}
