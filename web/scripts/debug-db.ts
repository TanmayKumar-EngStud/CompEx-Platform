
import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function main() {
    console.log('--- ExamTypes ---')
    const exams = await prisma.examtypes.findMany()
    console.log(exams)

    console.log('\n--- Sections ---')
    const sections = await prisma.sections.findMany()
    console.log(sections)
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
