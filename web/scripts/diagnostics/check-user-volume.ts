
import dotenv from 'dotenv';
dotenv.config({ path: '.env.production' });
import { prisma } from '../../shared/lib/prisma';

async function checkUserVolume() {
    try {
        const username = "tanmay_kumar";
        const user = await prisma.users.findUnique({ where: { username } });

        if (!user) {
            console.log("User not found: " + username);
            return;
        }

        const globalAttempts = await prisma.userattempts.count();
        console.log(`🌎 Global Attempts Count: ${globalAttempts}`);

        const mockAttemptCount = await prisma.usermocktestattempts.count({
            where: { userid: user.userid }
        });

        const attemptCount = await prisma.userattempts.count({
            where: { userid: user.userid }
        });

        console.log(`User: ${username} (ID: ${user.userid})`);
        console.log(`Total Practice Attempts: ${attemptCount}`);
        console.log(`Total Mock Attempts: ${mockAttemptCount}`);

    } catch (e) {
        console.error(e);
    } finally {
        await prisma.$disconnect();
    }
}

checkUserVolume();
