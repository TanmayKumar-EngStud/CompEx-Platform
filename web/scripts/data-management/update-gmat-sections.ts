
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
        }
    }
})

async function main() {
    console.log('🔄 Migrating GMAT section names to match UI...')

    // 1. Rename 'Quantitative' to 'Quants'
    const q = await prisma.sections.updateMany({
        where: { examtypeid: 2, name: 'Quantitative' },
        data: { name: 'Quants' }
    })
    console.log(`✅ Updated ${q.count} sections from Quantitative to Quants`)

    // 2. Rename 'Data Insights' to 'Integrated Reasoning'
    const di = await prisma.sections.updateMany({
        where: { examtypeid: 2, name: 'Data Insights' },
        data: { name: 'Integrated Reasoning' }
    })
    console.log(`✅ Updated ${di.count} sections from Data Insights to Integrated Reasoning`)
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
