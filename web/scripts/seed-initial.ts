
import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function main() {
    console.log('Seeding ExamTypes...')

    const gre = await prisma.examtypes.upsert({
        where: { examtypeid: 1 },
        update: {},
        create: {
            name: 'GRE',
            description: 'Graduate Record Examination'
        },
    })

    const gmat = await prisma.examtypes.upsert({
        where: { examtypeid: 2 },
        update: {},
        create: {
            name: 'GMAT',
            description: 'Graduate Management Admission Test'
        },
    })

    // Ensure 'quants' section exists for GRE (id 1)
    // Ensure 'quants' section exists for GRE (id 1)
    console.log('Seeding Sections...');
    const sections = [
        { sectionid: 101, examtypeid: 1, name: 'quants', description: 'Quantitative Reasoning' },
        { sectionid: 102, examtypeid: 1, name: 'verbal', description: 'Verbal Reasoning' }
    ];

    for (const section of sections) {
        await prisma.sections.upsert({
            where: { sectionid: section.sectionid },
            update: {},
            create: section
        });
    }
    console.log('Sections seeded.');

    console.log({ gre, gmat })
}

main()
    .then(async () => {
        await prisma.$disconnect()
    })
    .catch(async (e) => {
        console.error(e)
        await prisma.$disconnect()
        process.exit(1)
    })
