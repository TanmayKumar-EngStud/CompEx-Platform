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

async function fix() {
    console.log('🔄 Fixing problem fields in production...')

    // Update all problems that have isMockQuestion = true to false (for Explore page)
    // and set a default type if it's null or empty
    const result = await prisma.problems.updateMany({
        where: {
            OR: [
                { isMockQuestion: true },
                { type: null },
                { type: '' }
            ]
        },
        data: {
            isMockQuestion: false,
            type: 'Multiple Choice'
        }
    })

    console.log(`✅ Updated ${result.count} problems.`)
}

fix()
    .catch(console.error)
    .finally(() => prisma.$disconnect())
