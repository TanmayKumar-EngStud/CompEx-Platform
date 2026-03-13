
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function backfill() {
    console.log('Starting backfill...');

    const users = await prisma.users.findMany({ select: { userid: true } });
    console.log(`Found ${users.length} users to backfill.`);

    for (const user of users) {
        const attempts = await prisma.userattempts.findMany({
            where: { userid: user.userid },
            include: { problems: { select: { difficulty: true } } }
        });

        if (attempts.length === 0) continue;

        console.log(`Processing user ${user.userid}: ${attempts.length} attempts`);

        const stats: Record<number, { attempts: number, correct: number, time: number }> = {};

        for (const attempt of attempts) {
            if (!attempt.problems?.difficulty) continue;

            const difficulty = attempt.problems.difficulty;
            if (!stats[difficulty]) {
                stats[difficulty] = { attempts: 0, correct: 0, time: 0 };
            }

            stats[difficulty].attempts++;
            if (attempt.iscorrect) {
                stats[difficulty].correct++;
            }

            // Parse timetaken (assuming simple seconds or "MM:SS" format, simplifying for now as 0 if unknown)
            // If your timetaken is consistent string "MM:SS", parse it.
            // For now, let's treat time as 0 to avoid parsing errors blocking backfill 
            // unless we know the format.
            // stats[difficulty].time += ... 
        }

        for (const [diffLevel, data] of Object.entries(stats)) {
            const difficulty = parseInt(diffLevel);

            await prisma.user_difficulty_stats.upsert({
                where: {
                    userid_difficulty_is_mock: {
                        userid: user.userid,
                        difficulty: difficulty,
                        is_mock: false
                    }
                },
                update: {
                    total_attempts: data.attempts,
                    total_correct: data.correct,
                    last_updated: new Date()
                },
                create: {
                    userid: user.userid,
                    difficulty: difficulty,
                    is_mock: false,
                    total_attempts: data.attempts,
                    total_correct: data.correct,
                    total_time: 0,
                    last_updated: new Date()
                }
            });
        }
    }

    console.log('Backfill complete!');
}

backfill()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
