import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';

async function exportData() {
    const prisma = new PrismaClient({
        datasources: {
            db: {
                url: "postgresql://compexe_admin:QuiZA.0310!@127.0.0.1:5433/compex-db"
            }
        }
    });

    try {
        console.log("🔗 Connecting to local DB...");

        const examTypes = await prisma.examtypes.findMany();
        const sections = await prisma.sections.findMany();
        const problemSets = await prisma.ProblemsSet.findMany();
        const problems = await prisma.problems.findMany();
        const options = await prisma.problemoptions.findMany();

        const data = {
            examTypes,
            sections,
            problemSets,
            problems,
            options
        };

        fs.writeFileSync('comp-ex-data-dump.json', JSON.stringify(data, null, 2));
        console.log("✅ Data exported to comp-ex-data-dump.json");
    } catch (e) {
        console.error("❌ Export failed:", e);
    } finally {
        await prisma.$disconnect();
    }
}

exportData();
