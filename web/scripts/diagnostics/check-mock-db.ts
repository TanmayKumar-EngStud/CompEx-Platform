
import { prisma } from '../../shared/lib/prisma';

async function checkMocks() {
    console.log('🔍 Checking database for Mock Tests...');

    try {
        const examTypes = await prisma.examtypes.findMany();
        console.log('📚 Exam Types:', examTypes);

        const mocks = await prisma.mocktests.findMany({
            include: {
                examtypes: true,
                mocksections: true
            }
        });

        console.log(`📝 Found ${mocks.length} mock tests.`);
        mocks.forEach(m => {
            console.log(`- [${m.mocktestid}] ${m.examtypes?.name || 'Unknown Exam'} (Date: ${m.date}) - Active: ${m.isactive}`);
        });

        if (mocks.length === 0) {
            console.warn('⚠️ No mock tests found in the database.');
        }

    } catch (error) {
        console.error('❌ Error checking database:', error);
    } finally {
        await prisma.$disconnect();
    }
}

checkMocks();
