/**
 * import-qgen-fresh.ts
 *
 * Imports QGen-FRESH JSON question files into CompEx production database.
 * Source: ~/Desktop/QGen-FRESH/log_json_files/paper/mega_papers/
 * Target: CompEx PostgreSQL (Neon) via Prisma
 *
 * Usage: cd ~/Desktop/CompEx && npx tsx scripts/data-management/import-qgen-fresh.ts
 */

import { PrismaClient, Prisma } from '@prisma/client'
import * as dotenv from 'dotenv'
import * as fs from 'fs'
import * as path from 'path'

// Load environment variables — use .env.production for Neon (same pattern as question-bot.ts)
dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: process.env.DATABASE_URL
        }
    }
})

// ============================================================================
// CONFIGURATION
// ============================================================================

const QGEN_FRESH_DIR = path.join(
    process.env.HOME || '/Users/tanmaykumar',
    'Desktop/QGen-FRESH/log_json_files/paper/mega_papers'
)

// Section ID mapping: QGen-FRESH section name → CompEx (examtypeid, sectionid)
const SECTION_MAP: Record<string, Record<string, { examtypeid: number; sectionid: number }>> = {
    GRE: {
        'Quants': { examtypeid: 1, sectionid: 101 },
        'Verbal': { examtypeid: 1, sectionid: 102 },
    },
    GMAT: {
        'Quants': { examtypeid: 2, sectionid: 201 },
        'Quantitative': { examtypeid: 2, sectionid: 201 },
        'Verbal': { examtypeid: 2, sectionid: 202 },
        'Integrated Reasoning': { examtypeid: 2, sectionid: 203 },
        'Data Insights': { examtypeid: 2, sectionid: 203 },
    }
}

// Question type → CompEx type + options_type
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

// ============================================================================
// CACHES
// ============================================================================

// Cache for tag lookups: "tagName" → tagid
const tagCache = new Map<string, number>()

// Cache for tag_scope lookups: "tagid-examtypeid-sectionid" → tagScopeId
const tagScopeCache = new Map<string, number>()

// Deduplication cache: "title|examtypeid|sectionid" → true
const dedupeCache = new Set<string>()

// ============================================================================
// STATISTICS
// ============================================================================

let stats = {
    filesProcessed: 0,
    questionsInserted: 0,
    childrenInserted: 0,
    problemSetsCreated: 0,
    duplicatesSkipped: 0,
    errorsEncountered: 0,
    tagsCreated: 0,
    tagScopesCreated: 0,
}

// ============================================================================
// TAG RESOLUTION
// ============================================================================

/**
 * Parse a tag string like "topic: Ratio and Proportion" into { name, category }
 */
function parseTag(tagStr: string): { name: string; category: string } | null {
    const colonIndex = tagStr.indexOf(':')
    if (colonIndex === -1) return null

    const category = tagStr.substring(0, colonIndex).trim().toLowerCase()
    const name = tagStr.substring(colonIndex + 1).trim()

    if (!name || !category) return null

    // Normalize category names
    const categoryMap: Record<string, string> = {
        'topic': 'topic',
        'theme': 'theme',
        'question-type': 'type',
        'style': 'style',
        'skill': 'skill',
    }

    return {
        name,
        category: categoryMap[category] || category
    }
}

/**
 * Upsert a tag and return its tagid
 */
async function resolveTag(name: string, category: string): Promise<number> {
    const cacheKey = name
    if (tagCache.has(cacheKey)) {
        return tagCache.get(cacheKey)!
    }

    const tag = await prisma.tags.upsert({
        where: { name },
        update: { category },
        create: { name, category }
    })

    tagCache.set(cacheKey, tag.tagid)
    if (!tag.tagid) stats.tagsCreated++
    return tag.tagid
}

/**
 * Upsert a tag_scope and return its tagScopeId
 */
async function resolveTagScope(tagid: number, examtypeid: number, sectionid: number): Promise<number> {
    const cacheKey = `${tagid}-${examtypeid}-${sectionid}`
    if (tagScopeCache.has(cacheKey)) {
        return tagScopeCache.get(cacheKey)!
    }

    const scope = await prisma.tag_scopes.upsert({
        where: {
            tagid_examtypeid_sectionid: { tagid, examtypeid, sectionid }
        },
        update: {},
        create: { tagid, examtypeid, sectionid }
    })

    tagScopeCache.set(cacheKey, scope.tagScopeId)
    return scope.tagScopeId
}

/**
 * Resolve all tags for a question and return tagScopeIds
 */
async function resolveQuestionTags(
    tags: string[],
    examtypeid: number,
    sectionid: number
): Promise<number[]> {
    const tagScopeIds: number[] = []

    for (const tagStr of tags) {
        const parsed = parseTag(tagStr)
        if (!parsed) continue

        try {
            const tagid = await resolveTag(parsed.name, parsed.category)
            const tagScopeId = await resolveTagScope(tagid, examtypeid, sectionid)
            tagScopeIds.push(tagScopeId)
        } catch (err) {
            // Tag resolution failure is non-fatal — log and continue
            console.warn(`   ⚠️ Tag resolution failed for "${tagStr}":`, (err as Error).message)
        }
    }

    return tagScopeIds
}

// ============================================================================
// OPTIONS BUILDER
// ============================================================================

function buildOptions(
    options: Record<string, any> | null,
    answer: string | string[] | number | Record<string, string> | null
): { optiontext: string; iscorrect: boolean; group: string; explanation: string | null }[] {
    if (!options || options === null) {
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

    // Check if options use nested "blank N" structure (Text Completion)
    const firstKey = Object.keys(options)[0]
    const isNestedBlankStructure = firstKey && firstKey.toLowerCase().startsWith('blank')

    if (isNestedBlankStructure) {
        // NESTED: {"blank 1": {"A": {text, explanation}, "B": {...}}, "blank 2": {...}}
        const blankKeys = Object.keys(options).sort((a, b) => {
            const numA = parseInt(a.replace(/\D/g, '')) || 0
            const numB = parseInt(b.replace(/\D/g, '')) || 0
            return numA - numB
        })

        for (let i = 0; i < blankKeys.length; i++) {
            const blankKey = blankKeys[i]
            const blankOptions = options[blankKey]
            const groupNumber = String(i + 1) // "1", "2", "3" — matches TC-23.tsx expectation

            for (const [letterKey, val] of Object.entries(blankOptions as Record<string, any>)) {
                const hasText = typeof val === 'object' && val !== null && 'text' in val
                result.push({
                    optiontext: hasText ? val.text : String(val),
                    iscorrect: determineCorrect(letterKey, answer),
                    group: groupNumber,
                    explanation: hasText ? (val.explanation || null) : null
                })
            }
        }
    } else {
        // FLAT: {"A": {text, explanation}, "B": {...}, ...}
        for (const [key, val] of Object.entries(options)) {
            const hasText = typeof val === 'object' && val !== null && 'text' in val
            result.push({
                optiontext: hasText ? (val as any).text : String(val),
                iscorrect: determineCorrect(key, answer),
                group: key,
                explanation: hasText ? ((val as any).explanation || null) : null
            })
        }
    }

    return result
}

function determineCorrect(
    key: string,
    answer: string | string[] | number | Record<string, string> | null
): boolean {
    if (answer === null || answer === undefined) return false
    if (typeof answer === 'string') return key === answer
    if (Array.isArray(answer)) return answer.includes(key)
    // For numeric or object answers, no option is marked correct
    return false
}

// ============================================================================
// DEDUPLICATION
// ============================================================================

async function loadExistingTitles(): Promise<void> {
    console.log('📋 Loading existing question titles for deduplication...')
    const existing = await prisma.problems.findMany({
        where: {
            metadata: {
                path: ['generatedBy'],
                equals: 'QGen-FRESH-Import'
            }
        },
        select: {
            title: true,
            examtypeid: true,
            sectionid: true,
        }
    })

    for (const q of existing) {
        dedupeCache.add(`${q.title}|${q.examtypeid}|${q.sectionid}`)
    }
    console.log(`   Found ${existing.length} previously imported questions.`)
}

function isDuplicate(title: string, examtypeid: number, sectionid: number): boolean {
    return dedupeCache.has(`${title}|${examtypeid}|${sectionid}`)
}

function markInserted(title: string, examtypeid: number, sectionid: number): void {
    dedupeCache.add(`${title}|${examtypeid}|${sectionid}`)
}

// ============================================================================
// QUESTION INSERTION
// ============================================================================

/**
 * Insert a standard (non-parent) question
 */
async function insertStandardQuestion(
    q: any,
    examtypeid: number,
    sectionid: number
): Promise<number | null> {
    const title = (q.title || 'Untitled Question').substring(0, 200)

    if (isDuplicate(title, examtypeid, sectionid)) {
        stats.duplicatesSkipped++
        return null
    }

    const questionType = q['question-type'] || 'Multiple Choice'
    const typeInfo = TYPE_MAP[questionType] || { type: 'Multiple Choice', options_type: q.options_type || 'single' }

    const problem = await prisma.problems.create({
        data: {
            title,
            text: q.question || '',
            difficulty: q.difficulty || 3,
            sectionid,
            examtypeid,
            isMockQuestion: false,
            isActive: true,
            isChildren: false,
            type: typeInfo.type,
            options_type: typeInfo.options_type,
            prompt: q.prompt || null,
            solution: q.solution ? { text: q.solution, answer: q.answer } : Prisma.DbNull,
            metadata: {
                generatedBy: 'QGen-FRESH-Import',
                questionType,
                ...(q.metadata || {})
            },
            addedDate: new Date(),
            problemoptions: {
                create: buildOptions(q.options, q.answer)
            }
        }
    })

    // Link to tags
    const tagScopeIds = await resolveQuestionTags(q.tags || [], examtypeid, sectionid)
    for (const tagScopeId of tagScopeIds) {
        try {
            await prisma.problemtags.create({
                data: { problemid: problem.problemid, tagScopeId }
            })
        } catch {
            // Duplicate tag link — ignore
        }
    }

    markInserted(title, examtypeid, sectionid)
    stats.questionsInserted++
    return problem.problemid
}

/**
 * Insert a parent-child question set (RC, MSR, etc.)
 */
async function insertParentChildQuestion(
    parent: any,
    examtypeid: number,
    sectionid: number
): Promise<void> {
    const title = (parent.title || 'Untitled Set').substring(0, 200)

    if (isDuplicate(title, examtypeid, sectionid)) {
        stats.duplicatesSkipped++
        return
    }

    const questionType = parent['question-type'] || 'Reading Comprehension'

    // 1. Create ProblemsSet for the parent
    const problemsSet = await prisma.problemsSet.create({
        data: {
            title,
            type: questionType,
            sectionid,
            examtypeid,
            content: {
                passage: parent.metadata?.Passage || null,
                ...(parent.metadata || {}),
                generatedBy: 'QGen-FRESH-Import',
                questionType,
            },
            popularityIndex: 0,
        }
    })
    stats.problemSetsCreated++

    // Resolve parent tags for linking to all children
    const parentTagScopeIds = await resolveQuestionTags(parent.tags || [], examtypeid, sectionid)

    // Also link ProblemsSet to tags via problemssettags
    for (const tagScopeId of parentTagScopeIds) {
        try {
            await prisma.problemssettags.create({
                data: {
                    problemsSetId: problemsSet.problemsSetId,
                    tagScopeId
                }
            })
        } catch {
            // Duplicate — ignore
        }
    }

    // 2. Insert each child question
    const children = parent['child-questions'] || []
    for (const child of children) {
        try {
            const childTitle = (child.title || `${title} - Sub-question`).substring(0, 200)
            const childType = child['question-type'] || questionType
            const childTypeInfo = TYPE_MAP[childType] || { type: 'Multiple Choice', options_type: child.options_type || 'single' }

            const childProblem = await prisma.problems.create({
                data: {
                    title: childTitle,
                    text: child.question || '',
                    difficulty: child.difficulty || parent.difficulty || 3,
                    sectionid,
                    examtypeid,
                    isMockQuestion: false,
                    isActive: true,
                    isChildren: true,
                    problemsSetId: problemsSet.problemsSetId,
                    type: childTypeInfo.type,
                    options_type: childTypeInfo.options_type,
                    prompt: child.prompt || parent.prompt || null,
                    solution: child.solution ? { text: child.solution, answer: child.answer } : Prisma.DbNull,
                    metadata: {
                        generatedBy: 'QGen-FRESH-Import',
                        questionType: childType,
                        parentTitle: title,
                        ...(child.metadata || {})
                    },
                    addedDate: new Date(),
                    problemoptions: {
                        create: buildOptions(child.options, child.answer)
                    }
                }
            })

            // Link child to parent's tags + child's own tags
            const childTagScopeIds = await resolveQuestionTags(child.tags || [], examtypeid, sectionid)
            const allTagScopeIds = [...new Set([...parentTagScopeIds, ...childTagScopeIds])]

            for (const tagScopeId of allTagScopeIds) {
                try {
                    await prisma.problemtags.create({
                        data: { problemid: childProblem.problemid, tagScopeId }
                    })
                } catch {
                    // Duplicate — ignore
                }
            }

            stats.childrenInserted++
        } catch (err) {
            console.error(`   ❌ Child question error:`, (err as Error).message)
            stats.errorsEncountered++
        }
    }

    markInserted(title, examtypeid, sectionid)
}

// ============================================================================
// FILE PROCESSING
// ============================================================================

/**
 * Determine exam type from filename
 */
function getExamFromFilename(filename: string): string {
    if (filename.startsWith('GMAT')) return 'GMAT'
    if (filename.startsWith('GRE')) return 'GRE'
    return 'UNKNOWN'
}

/**
 * Process a single JSON file
 */
async function processFile(filepath: string): Promise<void> {
    const filename = path.basename(filepath)
    const exam = getExamFromFilename(filename)

    if (exam === 'UNKNOWN') {
        console.warn(`⚠️ Skipping unrecognized file: ${filename}`)
        return
    }

    console.log(`\n📄 Processing: ${filepath.replace(QGEN_FRESH_DIR + '/', '')}`)

    const raw = fs.readFileSync(filepath, 'utf-8')
    let data: any

    try {
        data = JSON.parse(raw)
    } catch {
        console.error(`   ❌ Failed to parse JSON: ${filename}`)
        stats.errorsEncountered++
        return
    }

    // Handle two wrapper formats:
    // Root files: { "1": { section, questions }, "2": ... }
    // Dated files: { "GMAT": { "1": { section, questions }, ... } }
    let sections: Record<string, any>
    if (data[exam]) {
        sections = data[exam]
    } else if (data['1'] || data['2'] || data['3'] || data['4']) {
        sections = data
    } else {
        console.warn(`   ⚠️ Unrecognized file structure in ${filename}`)
        return
    }

    for (const [sectionKey, sectionData] of Object.entries(sections)) {
        const sec = sectionData as any
        const sectionName = sec.section as string

        if (!sectionName) {
            console.warn(`   ⚠️ Section ${sectionKey} has no name — skipping`)
            continue
        }

        const mapping = SECTION_MAP[exam]?.[sectionName]
        if (!mapping) {
            console.warn(`   ⚠️ Unknown section "${sectionName}" for ${exam} — skipping`)
            continue
        }

        const { examtypeid, sectionid } = mapping
        const questions = sec.questions || []

        console.log(`   📚 ${exam} > ${sectionName}: ${questions.length} questions`)

        for (const q of questions) {
            try {
                if (q['child-questions'] && q['child-questions'].length > 0) {
                    // Parent-child question (RC, MSR, etc.)
                    await insertParentChildQuestion(q, examtypeid, sectionid)
                } else if (q.question) {
                    // Standard question
                    await insertStandardQuestion(q, examtypeid, sectionid)
                } else {
                    console.warn(`   ⚠️ Skipping question with no text and no children: "${q.title}"`)
                }
            } catch (err) {
                console.error(`   ❌ Question error ("${q.title?.substring(0, 50)}"): ${(err as Error).message}`)
                stats.errorsEncountered++
            }
        }
    }

    stats.filesProcessed++
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
    console.log('═══════════════════════════════════════════════════════════')
    console.log('  QGen-FRESH → CompEx Database Import')
    console.log('═══════════════════════════════════════════════════════════')
    console.log(`  Source: ${QGEN_FRESH_DIR}`)
    console.log(`  DB: ${process.env.DATABASE_URL?.split('@')[1] || 'unknown'}`)
    console.log('═══════════════════════════════════════════════════════════\n')

    // Test connection
    try {
        await prisma.$connect()
        console.log('✅ Database connected.\n')
    } catch (err) {
        console.error('❌ Database connection failed:', (err as Error).message)
        process.exit(1)
    }

    // Load existing questions for deduplication
    await loadExistingTitles()

    // Discover JSON files
    const filePaths: string[] = []

    // Root-level files
    const rootFiles = fs.readdirSync(QGEN_FRESH_DIR)
        .filter(f => f.endsWith('.json') && !f.startsWith('.'))
        .map(f => path.join(QGEN_FRESH_DIR, f))
    filePaths.push(...rootFiles)

    // Dated subdirectories
    const subdirs = fs.readdirSync(QGEN_FRESH_DIR)
        .filter(d => {
            const fullPath = path.join(QGEN_FRESH_DIR, d)
            return fs.statSync(fullPath).isDirectory()
        })

    for (const subdir of subdirs) {
        const subdirPath = path.join(QGEN_FRESH_DIR, subdir)
        const subFiles = fs.readdirSync(subdirPath)
            .filter(f => f.endsWith('.json'))
            .map(f => path.join(subdirPath, f))
        filePaths.push(...subFiles)
    }

    console.log(`\n📁 Found ${filePaths.length} JSON files to process.\n`)

    // Process each file
    for (const filepath of filePaths.sort()) {
        await processFile(filepath)
    }

    // Print summary
    console.log('\n═══════════════════════════════════════════════════════════')
    console.log('  IMPORT SUMMARY')
    console.log('═══════════════════════════════════════════════════════════')
    console.log(`  Files processed:      ${stats.filesProcessed}`)
    console.log(`  Questions inserted:   ${stats.questionsInserted}`)
    console.log(`  Children inserted:    ${stats.childrenInserted}`)
    console.log(`  ProblemSets created:  ${stats.problemSetsCreated}`)
    console.log(`  Duplicates skipped:   ${stats.duplicatesSkipped}`)
    console.log(`  Errors encountered:   ${stats.errorsEncountered}`)
    console.log(`  Tags resolved:        ${tagCache.size}`)
    console.log(`  TagScopes resolved:   ${tagScopeCache.size}`)
    console.log(`  ─────────────────────────────────────────────`)
    console.log(`  TOTAL RECORDS:        ${stats.questionsInserted + stats.childrenInserted}`)
    console.log('═══════════════════════════════════════════════════════════\n')
}

main()
    .then(async () => {
        await prisma.$disconnect()
        console.log('✅ Done. Database disconnected.')
    })
    .catch(async (e) => {
        console.error('❌ Fatal error:', e)
        await prisma.$disconnect()
        process.exit(1)
    })
