import { PrismaClient } from '@prisma/client';

async function checkCounts(url: string, name: string) {
    const prisma = new PrismaClient({
        datasources: {
            db: { url }
        }
    });

    try {
        const count = await prisma.problems.count();
        console.log(`📊 Database [${name}] (${url}): ${count} problems found.`);
    } catch (error: any) {
        console.error(`❌ Failed to connect to [${name}]:`, error.message);
    } finally {
        await prisma.$disconnect();
    }
}

async function main() {
    console.log("🔍 Checking local databases for questions...");
    await checkCounts("postgresql://compexe_admin:QuiZA.0310!@localhost:5433/artilaries", "artilaries (.env)");
    await checkCounts("postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db", "compex-db (.env.local)");

    // Also check the cloud DB to see current status
    const cloudUrl = "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require";
    await checkCounts(cloudUrl, "Neon Cloud (Production)");
}

main();
