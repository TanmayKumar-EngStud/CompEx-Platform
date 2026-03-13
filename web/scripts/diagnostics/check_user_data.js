
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function checkUser(username) {
    console.log(`Checking records for user: ${username}`);
    const user = await prisma.users.findUnique({
        where: { username },
        include: {
            user_overall_performance: true,
            user_difficulty_stats: true,
        }
    });

    if (!user) {
        console.log('User not found');
        return;
    }

    console.log('User ID:', user.userid);
    console.log('Overall Performance:', user.user_overall_performance);
    console.log('Difficulty Stats Count:', user.user_difficulty_stats.length);

    try {
        const tagPerf = await prisma.user_tag_performance.findMany({
            where: { userid: user.userid },
            take: 5
        });
        console.log('Sample Tag Performance:', tagPerf);
    } catch (e) {
        console.error('Error fetching Tag Performance:', e.message);
    }

    try {
        const mockRankings = await prisma.mocktestrankings.findMany({
            where: { userid: user.userid },
            take: 5
        });
        console.log('Sample Mock Rankings:', mockRankings);
    } catch (e) {
        console.error('Error fetching Mock Rankings:', e.message);
    }
}

const username = process.argv[2] || 'user_5041';
checkUser(username).then(() => process.exit(0)).catch(e => {
    console.error(e);
    process.exit(1);
});
