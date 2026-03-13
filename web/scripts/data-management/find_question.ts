import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function findQuestion() {
    const setId = 232;
    const set = await prisma.problemsSet.findUnique({
        where: { problemsSetId: setId },
        select: {
            problemsSetId: true,
            title: true,
            content: true,
        },
    });

    console.log('ProblemsSet 232:', JSON.stringify(set, null, 2));

    await prisma.$disconnect();
}

findQuestion().catch((e) => {
    console.error(e);
    process.exit(1);
});
