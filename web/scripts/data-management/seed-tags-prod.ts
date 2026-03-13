import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: "postgresql://neondb_owner:npg_ckYb3qEerwA6@ep-square-king-ah4a82vb-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
        }
    }
})

async function main() {
    console.log('🚀 Starting tag seeding for Neon Production...')

    // 1. Ensure ExamType exists
    const gre = await prisma.examtypes.upsert({
        where: { examtypeid: 1 },
        update: { name: 'GRE' },
        create: { examtypeid: 1, name: 'GRE', description: 'Graduate Record Examination' }
    })
    console.log('✅ ExamType GRE confirmed.')

    // 2. Ensure Sections exist
    const quants = await prisma.sections.upsert({
        where: { sectionid: 101 },
        update: { name: 'quants' },
        create: { sectionid: 101, examtypeid: 1, name: 'quants', description: 'Quantitative Reasoning' }
    })
    const verbal = await prisma.sections.upsert({
        where: { sectionid: 102 },
        update: { name: 'verbal' },
        create: { sectionid: 102, examtypeid: 1, name: 'verbal', description: 'Verbal Reasoning' }
    })
    console.log('✅ Sections quants and verbal confirmed.')

    // 3. Create Tags
    const tagsData = [
        { name: 'Algebra', category: 'topic' },
        { name: 'Geometry', category: 'topic' },
        { name: 'Arithmetic', category: 'topic' },
        { name: 'Data Analysis', category: 'topic' },
        { name: 'Reading Comprehension', category: 'topic' },
        { name: 'Text Completion', category: 'topic' },
        { name: 'Sentence Equivalence', category: 'topic' },
        { name: 'Multiple Choice', category: 'type' },
        { name: 'Numeric Entry', category: 'type' },
        { name: 'Multiple Answer', category: 'type' },
    ]

    console.log('🌱 Seeding tags...')
    const seededTags = []
    for (const tag of tagsData) {
        const t = await prisma.tags.upsert({
            where: { name: tag.name },
            update: { category: tag.category },
            create: tag
        })
        seededTags.push(t)
    }
    console.log(`✅ Seeded ${seededTags.length} tags.`)

    // 4. Create Tag Scopes
    console.log('🗺️ Creating tag scopes...')
    const tagMap = new Map(seededTags.map(t => [t.name, t.tagid]))

    const scopes = [
        // Quants Topics
        { tagid: tagMap.get('Algebra')!, examtypeid: 1, sectionid: 101 },
        { tagid: tagMap.get('Geometry')!, examtypeid: 1, sectionid: 101 },
        { tagid: tagMap.get('Arithmetic')!, examtypeid: 1, sectionid: 101 },
        { tagid: tagMap.get('Data Analysis')!, examtypeid: 1, sectionid: 101 },
        // Verbal Topics
        { tagid: tagMap.get('Reading Comprehension')!, examtypeid: 1, sectionid: 102 },
        { tagid: tagMap.get('Text Completion')!, examtypeid: 1, sectionid: 102 },
        { tagid: tagMap.get('Sentence Equivalence')!, examtypeid: 1, sectionid: 102 },
        // Types (shared or specific)
        { tagid: tagMap.get('Multiple Choice')!, examtypeid: 1, sectionid: 101 },
        { tagid: tagMap.get('Multiple Choice')!, examtypeid: 1, sectionid: 102 },
        { tagid: tagMap.get('Numeric Entry')!, examtypeid: 1, sectionid: 101 },
    ]

    for (const scope of scopes) {
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
    console.log(`✅ Created tag scopes.`)

    // 5. Categorize existing problems (ID 301-310)
    console.log('🏷️ Categorizing migrated problems...')

    // Quants problems (IDs were 301, 302, 305, 306, 309, 310)
    // Verbal problems (IDs were 303, 304, 307, 308)
    // We'll update their sectionid to 101/102 and link them to tags

    const problemUpdates = [
        { id: 301, section: 101, topic: 'Algebra', type: 'Multiple Choice' },
        { id: 302, section: 101, topic: 'Geometry', type: 'Multiple Choice' },
        { id: 303, section: 102, topic: 'Reading Comprehension', type: 'Multiple Choice' },
        { id: 304, section: 102, topic: 'Text Completion', type: 'Multiple Choice' },
        { id: 305, section: 101, topic: 'Arithmetic', type: 'Numeric Entry' },
        { id: 306, section: 101, topic: 'Data Analysis', type: 'Multiple Answer' },
        { id: 307, section: 102, topic: 'Sentence Equivalence', type: 'Multiple Choice' },
        { id: 308, section: 102, topic: 'Reading Comprehension', type: 'Multiple Choice' },
        { id: 309, section: 101, topic: 'Algebra', type: 'Multiple Choice' },
        { id: 310, section: 101, topic: 'Geometry', type: 'Multiple Choice' },
    ]

    for (const update of problemUpdates) {
        // Update sectionid
        await prisma.problems.update({
            where: { problemid: update.id },
            data: { sectionid: update.section }
        })

        // Link to Title/Topic tag_scope
        const topicTagId = tagMap.get(update.topic)!
        const topicScope = await prisma.tag_scopes.findUnique({
            where: { tagid_examtypeid_sectionid: { tagid: topicTagId, examtypeid: 1, sectionid: update.section } }
        })

        if (topicScope) {
            await prisma.problemtags.upsert({
                where: { problemid_tagScopeId: { problemid: update.id, tagScopeId: topicScope.tagScopeId } },
                update: {},
                create: { problemid: update.id, tagScopeId: topicScope.tagScopeId }
            })
        }

        // Link to Type tag_scope
        const typeTagId = tagMap.get(update.type)!
        const typeScope = await prisma.tag_scopes.findUnique({
            where: { tagid_examtypeid_sectionid: { tagid: typeTagId, examtypeid: 1, sectionid: update.section } }
        })

        if (typeScope) {
            await prisma.problemtags.upsert({
                where: { problemid_tagScopeId: { problemid: update.id, tagScopeId: typeScope.tagScopeId } },
                update: {},
                create: { problemid: update.id, tagScopeId: typeScope.tagScopeId }
            })
        }
    }

    console.log('✨ Data categorization complete!')
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
