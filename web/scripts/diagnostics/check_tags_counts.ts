import { PrismaClient } from '@prisma/client';

async function checkTags(url: string, name: string) {
    const prisma = new PrismaClient({
        datasources: {
            db: { url }
        }
    });

    try {
        const tagCount = await prisma.tags.count();
        const scopeCount = await prisma.tag_scopes.count();
        const problemTagCount = await prisma.problemtags.count();
        console.log(`📊 Database [${name}]:`);
        console.log(`   - Tags: ${tagCount}`);
        console.log(`   - Tag Scopes: ${scopeCount}`);
        console.log(`   - Problem Tags: ${problemTagCount}`);
    } catch (error: any) {
        console.error(`❌ Failed to connect to [${name}]:`, error.message);
    } finally {
        await prisma.$disconnect();
    }
}

async function main() {
    const localCompexUrl = "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db";
    const localArtilariesUrl = "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/artilaries";
    const cloudUrl = "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require";

    console.log("🔍 Checking tag data...");
    await checkTags(localCompexUrl, "Local compex-db");
    await checkTags(localArtilariesUrl, "Local artilaries");
    await checkTags(cloudUrl, "Neon Cloud (Production)");
}

main();
