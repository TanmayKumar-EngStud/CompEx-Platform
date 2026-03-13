
import { getUserAnalytics } from '../../features/user-analytics/services/analytics.service';
import { prisma } from '../../shared/lib/configs/prisma';

async function main() {
    const username = 'tanmay_kumar'; // The user from the screenshot
    console.log(`🔍 Debugging Analytics for user: ${username}`);

    try {
        const data = await getUserAnalytics(username, "GRE");
        console.log('✅ Success! Data retrieved:');
        console.log(JSON.stringify(data, null, 2));
    } catch (error: any) {
        console.error('❌ Error caught:', error);
        console.error('Stack:', error.stack);
    } finally {
        await prisma.$disconnect();
    }
}

main();
