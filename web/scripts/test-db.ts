
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    try {
        console.log("Testing Prisma connection...");
        const examTypes = await prisma.examtypes.findMany();
        console.log("Connection successful!");
        console.log("Exam types found:", examTypes);

        const mockCount = await prisma.mocktests.count();
        console.log("Total mock tests:", mockCount);
    } catch (error) {
        console.error("Database connection failed:", error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
