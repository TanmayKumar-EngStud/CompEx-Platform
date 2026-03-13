
import { PrismaClient } from '@prisma/client';
import * as dotenv from 'dotenv';
import { confirm } from '@inquirer/prompts';

dotenv.config({ path: '.env.production', override: true });

const prisma = new PrismaClient();

const dbUrl = process.env.DATABASE_URL;
console.log(`🔌 Connected to DB: ${dbUrl ? (dbUrl.includes('@') ? '***' + dbUrl.split('@')[1] : 'Local/Unprotected') : 'UNDEFINED'}`);


async function main() {
    const startOfDay = new Date('2026-02-04T00:00:00.000Z');
    const endOfDay = new Date('2026-02-04T23:59:59.999Z');

    console.log(`🔍 Searching for questions created between:\n   ${startOfDay.toISOString()}\n   ${endOfDay.toISOString()}`);

    const count = await prisma.problems.count({
        where: {
            creationdate: {
                gte: startOfDay,
                lte: endOfDay
            }
        }
    });

    const countAdded = await prisma.problems.count({
        where: {
            addedDate: {
                gte: startOfDay,
                lte: endOfDay
            }
        }
    });

    console.log(`📊 Found ${count} questions (creationdate) on Feb 4th.`);
    console.log(`📊 Found ${countAdded} questions (addedDate) on Feb 4th.`);

    // Debug: Show recent questions to understand the time
    const recent = await prisma.problems.findMany({
        take: 5,
        orderBy: { creationdate: 'desc' },
        select: { problemid: true, creationdate: true, addedDate: true }
    });
    console.log("🕒 Most recent 5 questions:", recent);


    const total = await prisma.problems.count();
    console.log(`📊 Total questions in database: ${total}`);

    if (count === 0 && countAdded === 0) {
        console.log("✅ No specific Feb 4th questions found to delete.");
        return;
    }

    // Check command line args for --force to skip interactive prompt if needed, 
    // but better to just confirm if running manually. 
    // Since I am an agent, I will rely on the user command or auto-confirm if I am confident.
    // actually, for this specific request, I will just proceed with a dry run view first.

    if (process.argv.includes('--delete')) {
        const deleted = await prisma.problems.deleteMany({
            where: {
                creationdate: {
                    gte: startOfDay,
                    lte: endOfDay
                }
            }
        });
        console.log(`🗑️  Successfully deleted ${deleted.count} questions.`);
    } else {
        console.log("ℹ️  Run with --delete to actually perform the deletion.");
    }
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
