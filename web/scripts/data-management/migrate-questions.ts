import { PrismaClient } from '@prisma/client';

async function migrate() {
    // Local Prisma client (Targeting compex-db which has 10 questions)
    const localPrisma = new PrismaClient({
        datasources: {
            db: {
                url: "postgresql://compexe_admin:QuiZA.0310!@localhost:5433/compex-db"
            }
        }
    });

    // Cloud Prisma client (Targeting Neon Production)
    const cloudPrisma = new PrismaClient({
        datasources: {
            db: {
                url: "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
            }
        }
    });

    try {
        console.log("🔗 Connecting to databases...");

        // Test connections
        await localPrisma.$connect();
        await cloudPrisma.$connect();
        console.log("✅ Databases connected.");

        // 1. Migrate Exam Types
        console.log("📝 Migrating Exam Types...");
        const examTypes = await localPrisma.examtypes.findMany();
        for (const type of examTypes) {
            await cloudPrisma.examtypes.upsert({
                where: { examtypeid: type.examtypeid },
                update: type,
                create: type
            });
        }
        console.log(`✅ Migrated ${examTypes.length} Exam Types.`);

        // 2. Migrate Sections
        console.log("📝 Migrating Sections...");
        const sections = await localPrisma.sections.findMany();
        for (const section of sections) {
            await cloudPrisma.sections.upsert({
                where: { sectionid: section.sectionid },
                update: section,
                create: section
            });
        }
        console.log(`✅ Migrated ${sections.length} Sections.`);

        // 3. Migrate ProblemsSet
        console.log("📝 Migrating ProblemsSets...");
        const problemSets = await localPrisma.problemsSet.findMany();
        for (const set of problemSets) {
            await cloudPrisma.problemsSet.upsert({
                where: { problemsSetId: set.problemsSetId },
                update: set as any,
                create: set as any
            });
        }
        console.log(`✅ Migrated ${problemSets.length} ProblemSets.`);

        // 4. Migrate Problems
        console.log("📝 Migrating Problems...");
        const problems = await localPrisma.problems.findMany();
        const batchSize = 100;
        for (let i = 0; i < problems.length; i += batchSize) {
            const batch = problems.slice(i, i + batchSize);
            for (const prob of batch) {
                await cloudPrisma.problems.upsert({
                    where: { problemid: prob.problemid },
                    update: prob as any,
                    create: prob as any
                });
            }
            console.log(`   Processed ${Math.min(i + batchSize, problems.length)} / ${problems.length} problems...`);
        }
        console.log(`✅ Migrated ${problems.length} Problems.`);

        // 5. Migrate Options
        console.log("📝 Migrating Options...");
        const options = await localPrisma.problemoptions.findMany();
        for (let i = 0; i < options.length; i += batchSize) {
            const batch = options.slice(i, i + batchSize);
            for (const opt of batch) {
                await cloudPrisma.problemoptions.upsert({
                    where: { optionid: opt.optionid },
                    update: opt,
                    create: opt
                });
            }
            console.log(`   Processed ${Math.min(i + batchSize, options.length)} / ${options.length} options...`);
        }
        console.log(`✅ Migrated ${options.length} Options.`);

        console.log("🎉 DATA MIGRATION COMPLETE! 🚀");
    } catch (error) {
        console.error("❌ Migration failed:", error);
    } finally {
        await localPrisma.$disconnect();
        await cloudPrisma.$disconnect();
    }
}

migrate();
