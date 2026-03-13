import { PrismaClient } from '@prisma/client';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.production', override: true });

const prisma = new PrismaClient();
async function run() {
    const problems = await prisma.problems.findMany({
        select: {
            examtypeid: true,
            isMockQuestion: true,
            type: true
        }
    });

    const examTypes = await prisma.examtypes.findMany();
    const examMap = Object.fromEntries(examTypes.map(e => [e.examtypeid, e.name]));

    const summary: Record<string, any> = {};
    problems.forEach(p => {
        const examName = examMap[p.examtypeid!] || 'Unknown';
        if (!summary[examName]) summary[examName] = { total: 0, Practice: 0, Mock: 0 };
        summary[examName].total++;
        if (p.isMockQuestion === false && p.type === 'Practice') {
            summary[examName].Practice++;
        } else {
            summary[examName].Mock++;
        }
    });

    console.log('Problem distribution:');
    console.table(summary);

    const scopes = await prisma.tag_scopes.findMany({
        include: { examtypes: true }
    });

    const scopeSummary: Record<string, number> = {};
    scopes.forEach(s => {
        const name = s.examtypes.name;
        scopeSummary[name] = (scopeSummary[name] || 0) + 1;
    });

    console.log('Available scopes by Exam:');
    console.table(scopeSummary);
}
run().catch(console.error).finally(() => prisma.$disconnect());
