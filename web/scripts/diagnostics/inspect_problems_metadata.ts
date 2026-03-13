import { PrismaClient } from '@prisma/client';

async function inspectProblems() {
    const prisma = new PrismaClient({
        datasources: {
            db: {
                url: "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db"
            }
        }
    });

    try {
        const problems = await prisma.problems.findMany({
            take: 5
        });

        console.log("🔍 Inspecting problems metadata:");
        problems.forEach(p => {
            console.log(`\nProblem ID: ${p.problemid}`);
            console.log(`Title: ${p.title}`);
            console.log(`Metadata: ${JSON.stringify(p.metadata, null, 2)}`);
        });
    } catch (error: any) {
        console.error("❌ Error:", error.message);
    } finally {
        await prisma.$disconnect();
    }
}

inspectProblems();
