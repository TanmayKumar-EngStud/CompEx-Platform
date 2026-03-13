
import { prisma } from '../../shared/lib/prisma';

async function seedMocks() {
    console.log('🌱 Seeding Mock Tests...');

    try {
        const greExam = await prisma.examtypes.findFirst({ where: { name: 'GRE' } });
        const gmatExam = await prisma.examtypes.findFirst({ where: { name: 'GMAT' } });

        if (!greExam || !gmatExam) {
            console.error('❌ GRE or GMAT exam types not found. Run basic seed first.');
            return;
        }

        const mocks = [
            {
                examtypeid: greExam.examtypeid,
                date: new Date(),
                starttime: new Date('2024-01-01T09:00:00Z'),
                endtime: new Date('2024-01-01T12:00:00Z'),
                isactive: true,
                difficulty: 3,
                description: "Full-length GRE Mock Test 1",
            },
            {
                examtypeid: greExam.examtypeid,
                date: new Date(new Date().setDate(new Date().getDate() + 1)), // Tomorrow
                starttime: new Date('2024-01-02T14:00:00Z'),
                endtime: new Date('2024-01-02T17:00:00Z'),
                isactive: true,
                difficulty: 4,
                description: "Advanced GRE Mock Test 2",
            },
            {
                examtypeid: gmatExam.examtypeid,
                date: new Date(),
                starttime: new Date('2024-01-01T10:00:00Z'),
                endtime: new Date('2024-01-01T13:00:00Z'),
                isactive: true,
                difficulty: 3,
                description: "Standard GMAT Mock Test 1",
            }
        ];

        for (const mock of mocks) {
            const created = await prisma.mocktests.create({
                data: {
                    examtypeid: mock.examtypeid,
                    date: mock.date,
                    starttime: mock.starttime,
                    endtime: mock.endtime,
                    isactive: mock.isactive,
                    difficulty: mock.difficulty,
                }
            });
            console.log(`✅ Created Mock Test ID: ${created.mocktestid} (${mock.description})`);
        }

    } catch (error) {
        console.error('❌ Error seeding mocks:', error);
    } finally {
        await prisma.$disconnect();
    }
}

seedMocks();
