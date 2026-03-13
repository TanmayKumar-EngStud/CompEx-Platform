
import { PrismaClient } from '@prisma/client'
import * as dotenv from 'dotenv'

dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: { db: { url: process.env.DATABASE_URL } }
})

async function inspectLatestQuestions() {
    const problems = await prisma.problems.findMany({
        orderBy: { addedDate: 'desc' },
        take: 2,
        include: {
            problemoptions: true,
            examtypes: true,
            sections: true
        }
    });

    if (problems.length === 0) {
        console.log("No problems found.");
        return;
    }

    console.log(`\n🔎 Inspecting latest ${problems.length} questions...\n`);

    for (const p of problems) {
        console.log('---------------------------------------------------');
        console.log(`ID: ${p.problemid} | Type: ${p.examtypes?.name || 'N/A'} [${p.isMockQuestion ? 'MOCK' : 'PRACTICE'}]`);
        console.log(`Title: ${p.title}`);
        console.log(`Difficulty: ${p.difficulty}`);
        console.log(`\nText:\n${p.text}`);

        console.log(`\nOptions:`);
        p.problemoptions.forEach(opt => {
            console.log(`  [${opt.group}] ${opt.iscorrect ? '✅' : ' '} ${opt.optiontext}`);
        });

        const meta = p.metadata as any;
        if (meta?.explanation) {
            console.log(`\n💡 Explanation:\n${meta.explanation.substring(0, 500)}...`);
        } else {
            console.log(`\n💡 Explanation: (Missing or not in metadata)`);
        }
        console.log('---------------------------------------------------\n');
    }
}

inspectLatestQuestions()
    .catch(console.error)
    .finally(() => prisma.$disconnect());
