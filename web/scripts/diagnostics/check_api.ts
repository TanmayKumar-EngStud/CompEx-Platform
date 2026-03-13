import { getProblemsForPagination } from '../features/question-solving/services/question-queries';
import { prisma } from '../shared/lib/configs/prisma';

async function main() {
    console.log('--- DB STATE ---');
    const sections = await prisma.sections.findMany();
    console.log('Available Sections:', sections.map(s => `${s.sectionid}: ${s.name} (Exam ${s.examtypeid})`));

    const tests = [
        { examName: 'GRE', sectionName: 'quants', examId: 1, sectionId: 10 },
        { examName: 'GRE', sectionName: 'verbal', examId: 1, sectionId: 11 },
        { examName: 'GMAT', sectionName: 'quants', examId: 2, sectionId: 7 },
        { examName: 'GMAT', sectionName: 'verbal', examId: 2, sectionId: 8 },
        { examName: 'GMAT', sectionName: 'integrated reasoning', examId: 2, sectionId: 9 },
    ];

    for (const t of tests) {
        console.log(`\nTesting ${t.examName} ${t.sectionName}...`);
        try {
            const res = await getProblemsForPagination(7530, t.examId, t.sectionId, {});
            console.log(`  Count: ${res.problemData.length}, Total: ${res.totalProblems}`);
            if (res.problemData.length > 0) {
                console.log(`  First item: ${res.problemData[0].title}`);
            }
        } catch (e: any) {
            console.error(`  Error: ${e.message}`);
        }
    }
}

main().catch(console.error);
