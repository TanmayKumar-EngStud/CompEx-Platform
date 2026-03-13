import dotenv from 'dotenv';
dotenv.config({ path: '.env.production' });

async function runTest() {
    console.log("🧪 Running Smoke Test: Analytics Connection...");
    try {
        const { getUserAnalytics } = await import('../../features/user-analytics/services/analytics.service');
        const data = await getUserAnalytics("tanmay_kumar", "GRE");

        if (!data || !data.user) {
            throw new Error("Test Failed: No data returned for existing user.");
        }

        console.log("✅ Smoke Test Passed: Connection established and data retrieved.");
        process.exit(0);
    } catch (error: any) {
        console.error("❌ Smoke Test Failed!");
        console.error(error.message);
        process.exit(1);
    }
}

runTest();
