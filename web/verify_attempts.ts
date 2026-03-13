
import { prisma } from "@/shared/lib/configs/prisma";

async function verifyAttempts() {
    const mockId = 13; // From screenshot

    try {
        console.log(`Checking attempts for Mock ID: ${mockId}`);

        const attempts = await prisma.usermocktestattempts.findMany({
            where: {
                mocktestid: mockId
            },
            select: {
                attemptid: true,
                userid: true,
                totalscore: true,
                isofficialattempt: true,
                starttime: true,
                endtime: true
            }
        });

        console.log(`Found ${attempts.length} attempts:`);
        attempts.forEach(att => {
            console.log(JSON.stringify(att, null, 2));
        });

        if (attempts.length === 0) {
            console.log("No attempts found.");
        }

    } catch (e) {
        console.error("Error querying DB:", e);
    } finally {
        await prisma.$disconnect();
    }
}

verifyAttempts();
