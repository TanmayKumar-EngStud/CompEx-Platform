
import { prisma } from '../../shared/lib/prisma';

async function cleanupOldQuestions() {
    const cutoffDate = new Date('2026-02-04T00:00:00.000Z');
    const isDeleteMode = process.argv.includes('--delete');

    try {
        console.log(`🔍 Analyzing 'problems' table...`);
        console.log(`📅 Cutoff Date: ${cutoffDate.toISOString()}`);

        const totalQuestions = await prisma.problems.count();
        const totalProblemSets = await prisma.problemsSet.count();
        const oldQuestionsCount = await prisma.problems.count({
            where: {
                creationdate: {
                    lt: cutoffDate
                }
            }
        });

        console.log(`----------------------------------------`);
        console.log(`📊 Total Questions: ${totalQuestions}`);
        console.log(`📊 Total Problem Sets: ${totalProblemSets}`);
        console.log(`🗑️  Questions to Delete (Created < Feb 3rd): ${oldQuestionsCount}`);
        console.log(`----------------------------------------`);

        if (oldQuestionsCount === 0) {
            console.log("✅ No old questions found. Database is clean.");
            return;
        }

        if (isDeleteMode) {
            console.log("🚀 DELETE mode active. Deleting...");
            const result = await prisma.problems.deleteMany({
                where: {
                    creationdate: {
                        lt: cutoffDate
                    }
                }
            });
            console.log(`✅ Successfully deleted ${result.count} questions.`);
        } else {
            console.log("⚠️  DRY RUN ONLY. No data was deleted.");
            console.log("👉 Run with --delete to execute deletion.");
        }

    } catch (error) {
        console.error("❌ Error during cleanup:", error);
    } finally {
        await prisma.$disconnect();
    }
}

cleanupOldQuestions();
