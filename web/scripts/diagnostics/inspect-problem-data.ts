
import { PrismaClient } from '@prisma/client'
import * as dotenv from 'dotenv'

dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: process.env.DATABASE_URL
        }
    }
})

async function inspect() {
    console.log('🔍 Inspecting recent high-quality practice questions...')

    const problems = await prisma.problems.findMany({
        where: {
            isMockQuestion: false
        },
        take: 3,
        orderBy: {
            problemid: 'desc'
        },
        include: {
            problemoptions: true,
            examtypes: true,
            sections: true
        }
    })

    problems.forEach(p => {
        console.log(`\n--- Problem ID: ${p.problemid} ("${p.title}") ---`)
        console.log(`Exam: ${p.examtypes?.name} | Section: ${p.sections?.name}`)
        console.log(`Type: ${p.type} | Options Type: ${p.options_type}`)
        console.log('Metadata:', JSON.stringify(p.metadata, null, 2))
        console.log('Solution:', JSON.stringify(p.solution, null, 2))
        console.log('Options:', p.problemoptions.map(o => `${o.group}: ${o.optiontext} [Correct: ${o.iscorrect}]`).join('\n'))
    })
}

inspect().catch(console.error).finally(() => prisma.$disconnect())
