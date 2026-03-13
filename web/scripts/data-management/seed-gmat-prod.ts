
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
        }
    }
})

async function main() {
    console.log('🚀 Starting GMAT seeding for Neon Production...')

    // 1. Ensure GMAT ExamType exists
    const gmat = await prisma.examtypes.upsert({
        where: { examtypeid: 2 },
        update: { name: 'GMAT' },
        create: { examtypeid: 2, name: 'GMAT', description: 'Graduate Management Admission Test' }
    })
    console.log('✅ ExamType GMAT confirmed.')

    // 2. Ensure Sections exist (Quantitative, Verbal, Data Insights)
    const quants = await prisma.sections.upsert({
        where: { sectionid: 201 },
        update: { name: 'Quantitative' },
        create: { sectionid: 201, examtypeid: 2, name: 'Quantitative', description: 'Quantitative Reasoning' }
    })
    const verbal = await prisma.sections.upsert({
        where: { sectionid: 202 },
        update: { name: 'Verbal' },
        create: { sectionid: 202, examtypeid: 2, name: 'Verbal', description: 'Verbal Reasoning' }
    })
    const dataInsights = await prisma.sections.upsert({
        where: { sectionid: 203 },
        update: { name: 'Data Insights' },
        create: { sectionid: 203, examtypeid: 2, name: 'Data Insights', description: 'Data Insights' }
    })
    console.log('✅ GMAT Sections confirmed.')

    // 3. Ensure Tags exist
    const gmatTags = [
        { name: 'Problem Solving', category: 'topic' },
        { name: 'Data Sufficiency', category: 'topic' },
        { name: 'Critical Reasoning', category: 'topic' },
        { name: 'Sentence Correction', category: 'topic' },
        { name: 'Mathematics', category: 'topic' },
        { name: 'Data Interpretation', category: 'topic' },
    ]

    const seededTags = []
    for (const tag of gmatTags) {
        const t = await prisma.tags.upsert({
            where: { name: tag.name },
            update: { category: tag.category },
            create: tag
        })
        seededTags.push(t)
    }

    // Also get existing tags to reuse (Algebra, Geometry, etc.)
    const existingTags = await prisma.tags.findMany()
    const tagMap = new Map(existingTags.map(t => [t.name, t.tagid]))

    // 4. Create Tag Scopes for GMAT
    console.log('🗺️ Creating GMAT tag scopes...')
    const scopes = [
        // Quantitative Topics
        { tagid: tagMap.get('Algebra')!, examtypeid: 2, sectionid: 201 },
        { tagid: tagMap.get('Geometry')!, examtypeid: 2, sectionid: 201 },
        { tagid: tagMap.get('Arithmetic')!, examtypeid: 2, sectionid: 201 },
        { tagid: tagMap.get('Problem Solving')!, examtypeid: 2, sectionid: 201 },
        { tagid: tagMap.get('Data Sufficiency')!, examtypeid: 2, sectionid: 201 },

        // Verbal Topics
        { tagid: tagMap.get('Reading Comprehension')!, examtypeid: 2, sectionid: 202 },
        { tagid: tagMap.get('Critical Reasoning')!, examtypeid: 2, sectionid: 202 },
        { tagid: tagMap.get('Sentence Correction')!, examtypeid: 2, sectionid: 202 },

        // Data Insights Topics
        { tagid: tagMap.get('Data Analysis')!, examtypeid: 2, sectionid: 203 },
        { tagid: tagMap.get('Data Interpretation')!, examtypeid: 2, sectionid: 203 },
    ]

    for (const scope of scopes) {
        if (!scope.tagid) continue;
        await prisma.tag_scopes.upsert({
            where: {
                tagid_examtypeid_sectionid: {
                    tagid: scope.tagid,
                    examtypeid: scope.examtypeid,
                    sectionid: scope.sectionid
                }
            },
            update: {},
            create: scope
        })
    }
    console.log(`✅ Created GMAT tag scopes.`)
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
