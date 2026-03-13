/**
 * seed-mock-papers.ts
 *
 * Imports QGen-FRESH JSON papers as mock papers into the CompEx production database.
 * Creates mocktests → mocksections → problems with isMockQuestion=true.
 *
 * Usage: cd ~/Desktop/compex && npx tsx scripts/data-management/seed-mock-papers.ts
 */

import { PrismaClient, Prisma } from '@prisma/client'
import * as dotenv from 'dotenv'
import * as fs from 'fs'
import * as path from 'path'

// Load .env.local for Neon DB
dotenv.config({ path: '.env.local', override: true })

const prisma = new PrismaClient({
    datasources: {
        db: { url: process.env.DATABASE_URL }
    }
})

// ============================================================================
// CONFIGURATION
// ============================================================================

const PAPERS_DIR = path.join(
    process.env.HOME || '/Users/tanmaykumar',
    'Desktop/QGen-FRESH/log_json_files/paper/mega_papers'
)

const MOCK_DIFFICULTY = 1

// exam name → examtypeid mapping
const EXAM_MAP: Record<string, number> = {
    GRE: 1,
    GMAT: 2,
}

// section name → sectionid mapping per exam (will be loaded dynamically)
let SECTION_MAP: Record<string, Record<string, number>> = {}

async function loadSectionMap() {
    const sections = await prisma.sections.findMany({
        include: { examtypes: { select: { name: true } } }
    })
    for (const s of sections) {
        const examName = s.examtypes?.name || 'UNKNOWN'
        if (!SECTION_MAP[examName]) SECTION_MAP[examName] = {}
        // Store both original name and titlecase version for matching
        SECTION_MAP[examName][s.name] = s.sectionid
        SECTION_MAP[examName][s.name.charAt(0).toUpperCase() + s.name.slice(1)] = s.sectionid
        SECTION_MAP[examName][s.name.toLowerCase()] = s.sectionid
    }
    console.log('📋 Section map loaded:', Object.keys(SECTION_MAP).map(e => `${e}: ${Object.keys(SECTION_MAP[e]).length} mappings`).join(', '))
}

// Question type → type + options_type
const TYPE_MAP: Record<string, { type: string; options_type: string }> = {
    'Problem Solving Simple': { type: 'Multiple Choice', options_type: 'single' },
    'Problem Solving Meta': { type: 'Multiple Choice', options_type: 'single' },
    'Quantitative Comparison': { type: 'Multiple Choice', options_type: 'single' },
    'Critical Reasoning': { type: 'Multiple Choice', options_type: 'single' },
    'Data Sufficiency': { type: 'Multiple Choice', options_type: 'single' },
    'Sentence Equivalence': { type: 'Multiple Choice', options_type: 'multi' },
    'Text Completion': { type: 'Multiple Choice', options_type: 'blank' },
    'Text Completion 1 Blank': { type: 'Multiple Choice', options_type: 'blank' },
    'Text Completion 2 Blanks': { type: 'Multiple Choice', options_type: 'blank' },
    'Text Completion 3 Blanks': { type: 'Multiple Choice', options_type: 'blank' },
    'Numerical Entry': { type: 'Numeric Entry', options_type: 'single' },
    'Reading Comprehension': { type: 'Multiple Choice', options_type: 'single' },
    'Graphic Interpretation': { type: 'Multiple Choice', options_type: 'single' },
    'Table Analysis': { type: 'Multiple Choice', options_type: 'single' },
    'Two-Part Analysis': { type: 'Multiple Choice', options_type: 'single' },
    'Multi-Source Reasoning': { type: 'Multiple Choice', options_type: 'single' },
}

// Tag caches
const tagCache = new Map<string, number>()
const tagScopeCache = new Map<string, number>()

// Stats
const stats = {
    mocktestsCreated: 0,
    sectionsCreated: 0,
    questionsInserted: 0,
    parentSetsInserted: 0,
    errorsEncountered: 0,
    tagsCreated: 0,
}

// ============================================================================
// TAG RESOLUTION (copied from import-qgen-fresh.ts)
// ============================================================================

function parseTag(tagStr: string): { name: string; category: string } | null {
    const parts = tagStr.split(':')
    if (parts.length < 2) return null
    const category = parts[0].trim()
    const name = parts.slice(1).join(':').trim()
    if (!category || !name) return null
    return { name, category }
}

async function resolveTag(name: string, category: string): Promise<number> {
    const cacheKey = `${category}:${name}`
    if (tagCache.has(cacheKey)) return tagCache.get(cacheKey)!

    const existing = await prisma.tags.findFirst({ where: { name } })
    if (existing) {
        tagCache.set(cacheKey, existing.tagid)
        return existing.tagid
    }

    const created = await prisma.tags.create({ data: { name, category } })
    tagCache.set(cacheKey, created.tagid)
    stats.tagsCreated++
    return created.tagid
}

async function resolveTagScope(tagid: number, examtypeid: number, sectionid: number): Promise<number> {
    const cacheKey = `${tagid}-${examtypeid}-${sectionid}`
    if (tagScopeCache.has(cacheKey)) return tagScopeCache.get(cacheKey)!

    const existing = await prisma.tag_scopes.findFirst({
        where: { tagid, examtypeid, sectionid }
    })
    if (existing) {
        tagScopeCache.set(cacheKey, existing.tagScopeId)
        return existing.tagScopeId
    }

    const created = await prisma.tag_scopes.create({
        data: { tagid, examtypeid, sectionid }
    })
    tagScopeCache.set(cacheKey, created.tagScopeId)
    return created.tagScopeId
}

async function resolveQuestionTags(tags: string[], examtypeid: number, sectionid: number): Promise<number[]> {
    const scopeIds: number[] = []
    for (const tagStr of tags) {
        const parsed = parseTag(tagStr)
        if (!parsed) continue
        try {
            const tagid = await resolveTag(parsed.name, parsed.category)
            const scopeId = await resolveTagScope(tagid, examtypeid, sectionid)
            scopeIds.push(scopeId)
        } catch { /* skip */ }
    }
    return scopeIds
}

// ============================================================================
// OPTIONS BUILDER (from import-qgen-fresh.ts)
// ============================================================================

// ============================================================================
// OPTIONS BUILDER (Corrected for TC/GI nested structures)
// ============================================================================

function buildOptions(
    options: Record<string, any> | null,
    answer: any
): { optiontext: string; iscorrect: boolean; group: string; explanation: string | null }[] {
    if (!options) {
        // Handle Numerical Entry: specific answer but no options list
        if (answer !== null && answer !== undefined && answer !== "") {
            return [{
                optiontext: String(answer),
                iscorrect: true,
                group: 'default',
                explanation: null
            }]
        }
        return []
    }
    const result: { optiontext: string; iscorrect: boolean; group: string; explanation: string | null }[] = []

    // Check if options use nested "blank N" structure (Text Completion, Graphic Interpretation)
    // Structure: { "blank 1": { "A": { text: "...", explanation: "..." }, "B": ... }, "blank 2": ... }
    const firstKey = Object.keys(options)[0]
    const isNestedBlankStructure = firstKey && (firstKey.toLowerCase().startsWith('blank') || firstKey.toLowerCase().includes('blank'))

    if (isNestedBlankStructure) {
        // NESTED STRUCTURE
        const blankKeys = Object.keys(options).sort((a, b) => {
            const numA = parseInt(a.replace(/\D/g, '')) || 0
            const numB = parseInt(b.replace(/\D/g, '')) || 0
            return numA - numB
        })

        for (let i = 0; i < blankKeys.length; i++) {
            const blankKey = blankKeys[i]
            const blankOptions = options[blankKey]
            // We strip non-digits to get "1" from "blank 1", "2" from "blank 2"
            // This matches strict group numbers "1", "2", "3" expected by TC-23 template
            const groupNumber = String(i + 1)

            for (const [letterKey, val] of Object.entries(blankOptions as Record<string, any>)) {
                // val might be string or object { text, explanation }
                const valObj = (typeof val === 'object' && val !== null) ? val : { text: String(val), explanation: null }

                result.push({
                    optiontext: valObj.text || String(val),
                    iscorrect: determineCorrect(letterKey, answer),
                    group: groupNumber,
                    explanation: valObj.explanation || null
                })
            }
        }
    } else {
        // FLAT STRUCTURE (Simple choice, Reading Comp, etc.)
        // Structure: { "A": "Option text", "B": { text: "Option text", ... } }
        for (const [key, val] of Object.entries(options)) {
            const valObj = (typeof val === 'object' && val !== null) ? val : { text: String(val), explanation: null }

            result.push({
                optiontext: valObj.text || String(val),
                iscorrect: determineCorrect(key, answer),
                group: 'default', // Flat options use default group
                explanation: valObj.explanation || null
            })
        }
    }

    return result
}

function determineCorrect(key: string, answer: any): boolean {
    if (!answer) return false

    // Case-insensitive comparison key
    const k = key.toUpperCase()

    if (typeof answer === 'string') return answer.toUpperCase() === k
    if (typeof answer === 'number') return String(answer) === key

    // Arrays: ["A", "B"] or ["C"]
    if (Array.isArray(answer)) {
        return answer.map(a => String(a).toUpperCase()).includes(k)
    }

    // Objects: sometimes answer might be { "blank 1": "A", "blank 2": "B" } (rare but possible in some formats)
    if (typeof answer === 'object') {
        return Object.values(answer).map(v => String(v).toUpperCase()).includes(k)
    }

    return false
}

// ============================================================================
// QUESTION INSERTION
// ============================================================================

async function insertQuestion(
    q: any,
    examtypeid: number,
    sectionid: number,
    mocksectionid: number,
    questionNumber: number
): Promise<number | null> {
    const title = (q.title || 'Untitled Question').substring(0, 200)
    const questionType = q['question-type'] || 'Multiple Choice'
    const typeInfo = TYPE_MAP[questionType] || { type: 'Multiple Choice', options_type: q.options_type || 'single' }

    const problem = await prisma.problems.create({
        data: {
            title,
            text: q.question || '',
            difficulty: q.difficulty || MOCK_DIFFICULTY,
            sectionid,
            examtypeid,
            isMockQuestion: true,
            isActive: true,
            isChildren: false,
            type: typeInfo.type,
            options_type: typeInfo.options_type,
            prompt: q.prompt || null,
            solution: q.solution ? { text: q.solution, answer: q.answer } : Prisma.DbNull,
            mockquestionnumber: questionNumber,
            mocksectionid: mocksectionid,
            metadata: {
                generatedBy: 'QGen-FRESH-MockSeed',
                questionType,
                ...(q.metadata || {})
            },
            addedDate: new Date(),
            problemoptions: {
                create: buildOptions(q.options, q.answer)
            }
        }
    })

    // Tags
    const tagScopeIds = await resolveQuestionTags(q.tags || [], examtypeid, sectionid)
    for (const tagScopeId of tagScopeIds) {
        try {
            await prisma.problemtags.create({ data: { problemid: problem.problemid, tagScopeId } })
        } catch { /* dup */ }
    }

    stats.questionsInserted++
    return problem.problemid
}

async function insertParentChild(
    parent: any,
    examtypeid: number,
    sectionid: number,
    mocksectionid: number,
    questionNumber: number
): Promise<void> {
    const title = (parent.title || 'Untitled Passage').substring(0, 200)
    const questionType = parent['question-type'] || 'Reading Comprehension'
    const typeInfo = TYPE_MAP[questionType] || { type: 'Multiple Choice', options_type: 'single' }

    // Create parent ProblemSet
    const problemsSet = await prisma.problemsSet.create({
        data: {
            title,
            type: typeInfo.type,
            content: parent.metadata || {},
            sectionid,
            examtypeid,
            mockquestionnumber: questionNumber,
            mocksectionid: mocksectionid,
        }
    })

    // Tags on parent
    const tagScopeIds = await resolveQuestionTags(parent.tags || [], examtypeid, sectionid)
    for (const tagScopeId of tagScopeIds) {
        try {
            await prisma.problemssettags.create({
                data: { problemsSetId: problemsSet.problemsSetId, tagScopeId }
            })
        } catch { /* dup */ }
    }

    // Insert child questions
    const children = parent['child-questions'] || parent.questions || []
    let childNum = 1
    for (const child of children) {
        const childTitle = (child.title || `${title} - Q${childNum}`).substring(0, 200)
        const childType = child['question-type'] || questionType
        const childTypeInfo = TYPE_MAP[childType] || { type: 'Multiple Choice', options_type: child.options_type || 'single' }

        await prisma.problems.create({
            data: {
                title: childTitle,
                text: child.question || '',
                difficulty: child.difficulty || MOCK_DIFFICULTY,
                sectionid,
                examtypeid,
                isMockQuestion: true,
                isActive: true,
                isChildren: true,
                problemsSetId: problemsSet.problemsSetId,
                type: childTypeInfo.type,
                options_type: childTypeInfo.options_type,
                prompt: child.prompt || null,
                solution: child.solution ? { text: child.solution, answer: child.answer } : Prisma.DbNull,
                mockquestionnumber: questionNumber,
                mocksectionid: mocksectionid,
                metadata: {
                    generatedBy: 'QGen-FRESH-MockSeed',
                    questionType: childType,
                    ...(child.metadata || {})
                },
                addedDate: new Date(),
                problemoptions: {
                    create: buildOptions(child.options, child.answer)
                }
            }
        })
        stats.questionsInserted++
        childNum++
    }

    stats.parentSetsInserted++
}

// ============================================================================
// MAIN
// ============================================================================

async function seedMockPaper(filename: string, exam: string) {
    const filepath = path.join(PAPERS_DIR, filename)
    if (!fs.existsSync(filepath)) {
        console.error(`❌ File not found: ${filepath}`)
        return
    }

    const examtypeid = EXAM_MAP[exam]
    if (!examtypeid) {
        console.error(`❌ Unknown exam: ${exam}`)
        return
    }

    console.log(`\n🎯 Seeding ${exam} mock paper from ${filename}`)

    // Parse JSON
    const data = JSON.parse(fs.readFileSync(filepath, 'utf-8'))

    // Data format: { "1": { section: "Quants", questions: [...] }, "2": ... }
    // or { "GRE": { "1": ... } }
    let sections: Record<string, any>
    if (data[exam]) {
        sections = data[exam]
    } else if (data['1'] || data['2'] || data['3'] || data['4']) {
        sections = data
    } else {
        console.error(`❌ Unrecognized structure in ${filename}`)
        return
    }

    // 1. Create mocktest
    const mocktest = await prisma.mocktests.create({
        data: {
            examtypeid,
            difficulty: MOCK_DIFFICULTY,
            date: new Date(),
            starttime: new Date(),
            endtime: new Date(),
            isactive: true,
        }
    })
    console.log(`   ✅ Created MockTest ID: ${mocktest.mocktestid} for ${exam}`)
    stats.mocktestsCreated++

    // 2. Process each section
    const sortedKeys = Object.keys(sections).sort((a, b) => {
        const na = parseInt(a), nb = parseInt(b)
        if (!isNaN(na) && !isNaN(nb)) return na - nb
        return a.localeCompare(b)
    })

    let sectionNumber = 1
    for (const sectionKey of sortedKeys) {
        const sec = sections[sectionKey]
        const sectionName = sec.section as string
        if (!sectionName) {
            console.warn(`   ⚠️ Section ${sectionKey} has no name — skipping`)
            continue
        }

        const sectionid = SECTION_MAP[exam]?.[sectionName]
        if (!sectionid) {
            console.warn(`   ⚠️ Unknown section "${sectionName}" for ${exam} — skipping`)
            continue
        }

        // Create mocksection
        const mocksection = await prisma.mocksections.create({
            data: {
                mocktestid: mocktest.mocktestid,
                sectionnumber: sectionNumber,
                sectionid,
            }
        })
        console.log(`   📋 Created MockSection ${sectionNumber}: ${sectionName} (ID: ${mocksection.mocksectionid})`)
        stats.sectionsCreated++

        // Insert questions
        const questions = sec.questions || []
        let questionNumber = 1

        for (const q of questions) {
            try {
                if (q['child-questions'] && q['child-questions'].length > 0) {
                    await insertParentChild(q, examtypeid, sectionid, mocksection.mocksectionid, questionNumber)
                } else if (q.question) {
                    await insertQuestion(q, examtypeid, sectionid, mocksection.mocksectionid, questionNumber)
                } else {
                    console.warn(`   ⚠️ Skipping question with no text: "${q.title?.substring(0, 50)}"`)
                    continue
                }
                questionNumber++
            } catch (err) {
                console.error(`   ❌ Error inserting "${q.title?.substring(0, 50)}": ${(err as Error).message}`)
                stats.errorsEncountered++
            }
        }

        console.log(`   ✅ Inserted ${questionNumber - 1} questions for ${sectionName}`)
        sectionNumber++
    }
}

async function main() {
    console.log('🚀 Mock Paper Seeder')
    console.log('='.repeat(60))
    console.log(`📁 Source: ${PAPERS_DIR}`)
    console.log(`🎯 Difficulty: ${MOCK_DIFFICULTY}`)
    console.log()

    // Load section mappings from DB
    await loadSectionMap()

    // Clean up existing mocks to prevent duplicates
    console.log('🧹 Cleaning up existing mock tests...')
    const examTypeIds = [EXAM_MAP['GRE'], EXAM_MAP['GMAT']]
    // Delete mocks with same difficulty and exam types
    const deleted = await prisma.mocktests.deleteMany({
        where: {
            examtypeid: { in: examTypeIds },
            difficulty: MOCK_DIFFICULTY
        }
    })
    console.log(`   Deleted ${deleted.count} old mock tests.`)

    // Seed GRE mock paper
    await seedMockPaper('GRE_1.json', 'GRE')

    // Seed GMAT mock paper
    await seedMockPaper('GMAT_1.json', 'GMAT')

    console.log('\n' + '='.repeat(60))
    console.log('📊 Summary:')
    console.log(`   Mock Tests Created: ${stats.mocktestsCreated}`)
    console.log(`   Sections Created:   ${stats.sectionsCreated}`)
    console.log(`   Questions Inserted: ${stats.questionsInserted}`)
    console.log(`   Parent Sets:        ${stats.parentSetsInserted}`)
    console.log(`   Tags Created:       ${stats.tagsCreated}`)
    console.log(`   Errors:             ${stats.errorsEncountered}`)
}

main()
    .then(async () => {
        await prisma.$disconnect()
        console.log('\n✅ Done. Database disconnected.')
    })
    .catch(async (e) => {
        console.error('❌ Fatal error:', e)
        await prisma.$disconnect()
        process.exit(1)
    })
