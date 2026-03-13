
import dotenv from 'dotenv';
dotenv.config({ path: '.env.production' });
import { prisma } from '../../shared/lib/prisma';

async function checkRegistrations() {
    const start = new Date('2026-02-04T00:00:00Z');
    const end = new Date('2026-02-05T23:59:59Z');

    console.log(`🔍 Checking registrations between ${start.toISOString()} and ${end.toISOString()}...`);

    const newUsers = await prisma.users.findMany({
        where: {
            registrationdate: {
                gte: start,
                lte: end
            },
            email: {
                not: 'tanmay44a@gmail.com' // Exclude the user
            }
        },
        select: {
            username: true,
            email: true,
            registrationdate: true
        }
    });

    console.log(`✅ Found ${newUsers.length} new users.`);
    newUsers.forEach(u => console.log(`- ${u.username} (${u.email}) joined on ${u.registrationdate}`));
}

checkRegistrations()
    .catch(console.error)
    .finally(() => prisma.$disconnect());
