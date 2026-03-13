
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharva", "Dhruv", "Kabir", "Rohan", "Aryan", "Kian", "Rudra", "Om", "Jai",
    "Ananya", "Diya", "Sana", "Pari", "Aadhya", "Kiara", "Myra", "Amaira", "Prisha", "Riya",
    "Saanvi", "Samaira", "Zara", "Inaya", "Aarya", "Kyra", "Isha", "Sarah", "Nitya", "Tara",
    "Vikram", "Rahul", "Amit", "Suresh", "Ramesh", "Sanjay", "Vijay", "Rajesh", "Manish", "Alok"
];

const LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Patel", "Kumar", "Mehta", "Malhotra", "Reddy", "Nair",
    "Chopra", "Kapoor", "Jain", "Agarwal", "Bhatia", "Saxena", "Mishra", "Dubey", "Pandey", "Tiwari",
    "Yadav", "Das", "Jha", "Chaudhary", "Sinha", "Ray", "Bose", "Ghosh", "Datta", "Bakshi"
];

function getRandomName() {
    const first = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
    const last = LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
    return { first, last, full: `${first}_${last}`.toLowerCase() };
}

async function main() {
    console.log('🚀 Starting username fix for generic users...');

    // Find users with "user_" prefix or strictly numeric/generic names
    const genericUsers = await prisma.users.findMany({
        where: {
            OR: [
                { username: { startsWith: 'user_' } },
                { username: { startsWith: 'testuser' } }
            ]
        }
    });

    console.log(`Found ${genericUsers.length} generic users to rename.`);

    for (const user of genericUsers) {
        let newName = getRandomName();
        let isUnique = false;
        let attempts = 0;

        // Ensure uniqueness
        while (!isUnique && attempts < 10) {
            const existing = await prisma.users.findFirst({
                where: { username: { equals: newName.full, mode: 'insensitive' } }
            });
            if (!existing) {
                isUnique = true;
            } else {
                newName = getRandomName();
                // Append random number if colliding often
                if (attempts > 5) newName.full += Math.floor(Math.random() * 100);
            }
            attempts++;
        }

        if (isUnique) {
            console.log(`✨ Renaming ${user.username} -> ${newName.full}`);
            await prisma.users.update({
                where: { userid: user.userid },
                data: {
                    username: newName.full,
                    // Also update image to matching avatar if needed
                    image_url: `https://api.dicebear.com/7.x/avataaars/svg?seed=${newName.full}`
                }
            });
        } else {
            console.log(`❌ Could not find unique name for ${user.username} after 10 attempts.`);
        }
    }

    console.log('✅ Username fix complete!');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
