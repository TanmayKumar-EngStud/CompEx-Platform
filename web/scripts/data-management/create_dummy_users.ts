
import { PrismaClient } from '@prisma/client';
import crypto from 'crypto';

const prisma = new PrismaClient();

async function main() {
    console.log('🌱 Starting to create 15 dummy users...');

    const usersToCreate = Array.from({ length: 15 }).map((_, i) => {
        const hash = crypto.randomBytes(4).toString('hex').toUpperCase(); // Generate 8-char hex hash
        const username = `Dummy_A_${hash}`;

        return {
            username: username,
            email: `${username.toLowerCase()}@example.com`,
            password: 'password123', // Default password for all dummy users
        };
    });

    let createdCount = 0;

    for (const user of usersToCreate) {
        try {
            await prisma.users.create({
                data: user,
            });
            console.log(`✅ Created user: ${user.username}`);
            createdCount++;
        } catch (e) {
            console.error(`❌ Failed to create user ${user.username}:`, e);
        }
    }

    console.log(`\n🎉 Finished! Successfully created ${createdCount} dummy users.`);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
