
import dotenv from 'dotenv';
dotenv.config({ path: '.env.production' });
console.log("📍 ENV Loaded. DB URL Masked:", process.env.DATABASE_URL?.replace(/:[^@]*@/, ':****@'));

async function debugAnalytics() {
    const { getUserAnalytics } = await import('../../features/user-analytics/services/analytics.service');
    const { prisma } = await import('../../shared/lib/prisma');
    console.log("🔍 Starting Analytics Debug for 'tanmay_kumar'...");
    try {
        const data = await getUserAnalytics("tanmay_kumar", "GRE");
        console.log("✅ Success! Data returned:");
        console.log(JSON.stringify(data, null, 2));
    } catch (error: any) {
        console.error("❌ CRASHED!");
        console.error("Message:", error.message);
        console.error("Stack:", error.stack);
    } finally {
        await prisma.$disconnect();
    }
}

debugAnalytics();
