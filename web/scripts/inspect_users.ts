
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    console.log('🔍 Inspecting users in the database...');

    const count = await prisma.users.count();
    console.log(`Total users: ${count}`);

    const users = await prisma.users.findMany({
        take: 50,
        orderBy: { userid: 'desc' },
        select: { userid: true, username: true, email: true }
    });

    console.log('Latest 50 users:');
    console.table(users);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
