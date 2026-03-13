
const { prisma } = require('../shared/lib/configs/prisma');

async function test() {
    console.log('Prisma users model:', prisma.users ? 'Found' : 'Missing');
    if (prisma.users) {
        const count = await prisma.users.count();
        console.log('User count:', count);
    } else {
        console.log('Keys in prisma:', Object.keys(prisma).filter(k => !k.startsWith('$')));
    }
}

test().then(() => process.exit(0)).catch(e => {
    console.error(e);
    process.exit(1);
});
