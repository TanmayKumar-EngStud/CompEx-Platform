
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
    console.log('Prisma models:', Object.keys(prisma).filter(k => !k.startsWith('$') && !k.startsWith('_')));
    try {
        const userCount = await prisma.users.count();
        console.log('Users count:', userCount);
    } catch (e) {
        console.error('Failed to access users:', e.message);
    }
    process.exit(0);
}

main();
