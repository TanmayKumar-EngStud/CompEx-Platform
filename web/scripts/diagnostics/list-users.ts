
import dotenv from 'dotenv';
dotenv.config({ path: '.env.production' });
import { prisma } from '../../shared/lib/prisma';

async function listUsers() {
    try {
        const users = await prisma.users.findMany({
            select: { username: true, userid: true },
            take: 50,
            orderBy: { registrationdate: 'desc' }
        });
        console.log("Users found:");
        users.forEach(u => console.log(`- ${u.username} (ID: ${u.userid})`));

    } catch (e) {
        console.error(e);
    } finally {
        await prisma.$disconnect();
    }
}

listUsers();
