import * as dotenv from 'dotenv';
import path from 'path';

// Load environment variables IMMEDIATELY before imports
dotenv.config({ path: path.join(process.cwd(), '.env') });

import { sendOtpEmail } from '../shared/lib/services/mail-service';

async function testEmail() {
    const testEmailAddress = process.env.TEST_EMAIL_RECIPIENT || 'tanmay44a@gmail.com';
    console.log(`🚀 Starting email test to: ${testEmailAddress}`);
    console.log(`Checking config:`);
    console.log(`- SMTP Host: ${process.env.SMTP_HOST}`);
    console.log(`- SMTP User: ${process.env.SMTP_USER}`);
    console.log(`- SMTP Port: ${process.env.SMTP_PORT}`);
    console.log(`- SMTP Secure: ${process.env.SMTP_SECURE}`);

    try {
        const success = await sendOtpEmail(testEmailAddress, '123456', 'signup');
        if (success) {
            console.log('✅ Test email sent successfully! Please check your inbox.');
        } else {
            console.log('❌ Failed to send test email. Check the error logs above.');
        }
    } catch (error) {
        console.error('💥 Critical error during email test:', error);
    }
}

testEmail();
