
import dotenv from 'dotenv';
import path from 'path';

// Explicitly load production env
dotenv.config({ path: path.resolve(process.cwd(), '.env.production') });

// Must import prisma AFTER loading env
import { PrismaClient } from '@prisma/client';
import { getUserAnalytics } from '../../features/user-analytics/services/analytics.service';

const prisma = new PrismaClient();

async function main() {
    console.log("🌍 Connecting to PRODUCTION database...");
    console.log(`URL: ${process.env.DATABASE_URL?.substring(0, 20)}...`);

    const username = 'tanmay_kumar';

    // 1. Check raw user existence
    const user = await prisma.users.findMany({
        where: {
            username: {
                contains: 'tanmay',
                mode: 'insensitive'
            }
        }
    });

    console.log(`\n🔎 Found ${user.length} users matching 'tanmay':`);
    user.forEach(u => console.log(` - ID: ${u.userid} | Username: ${u.username} | Email: ${u.email}`));

    if (user.length === 0) {
        console.error("❌ User not found in Production DB!");
        return;
    }

    // 2. Try getUserAnalytics for the specific match
    const targetUser = user.find(u => u.username === username);
    if (targetUser) {
        console.log(`\n🧪 Testing getUserAnalytics for '${username}'...`);
        try {
            // We need to inject the prisma instance usage since the service uses the singleton
            // But since we are running a script, we might run into the singleton using local .env if we are not careful.
            // However, the service imports `prisma` from `shared/lib/configs/prisma` which uses `global.prisma`.
            // We can try to shim it.
            // @ts-ignore
            global.prisma = prisma;

            const data = await getUserAnalytics(username, "GRE");
            console.log("✅ getUserAnalytics Result:");
            if (data) {
                console.log("   User:", data.user.username);
                console.log("   Analytics Keys:", Object.keys(data.analytics));
            } else {
                console.log("   Result is NULL");
            }
        } catch (error: any) {
            console.error("❌ getUserAnalytics THREW Error:", error.message);
            console.error(error.stack);
        }
    }
}

main()
    .catch(e => console.error(e))
    .finally(async () => {
        await prisma.$disconnect();
    });
