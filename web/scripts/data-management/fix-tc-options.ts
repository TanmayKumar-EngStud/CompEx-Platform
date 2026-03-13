/**
 * fix-tc-options.ts
 *
 * One-time repair script: fixes broken Text Completion question options
 * that were imported with "[object Object]" as optiontext.
 *
 * Root cause: buildOptions() in import-qgen-fresh.ts iterated top-level
 * "blank 1"/"blank 2"/"blank 3" keys instead of the nested A/B/C/D/E/F/G/H/I options.
 *
 * This script:
 * 1. Finds all TC questions with broken options in the DB
 * 2. Loads original QGen-FRESH JSON files to get correct option data
 * 3. Deletes broken problemoptions rows
 * 4. Inserts correct options with proper group ("1","2","3") and iscorrect flags
 * 5. Updates options_type to "blank"
 *
 * Usage: cd ~/Desktop/CompEx && npx tsx scripts/data-management/fix-tc-options.ts
 */

import { PrismaClient } from '@prisma/client'
import * as dotenv from 'dotenv'
import * as fs from 'fs'
import * as path from 'path'

dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: { db: { url: process.env.DATABASE_URL } }
})

const QGEN_DIR = path.join(
    process.env.HOME || '/Users/tanmaykumar',
    'Desktop/QGen-FRESH/log_json_files/paper/mega_papers'
)

// ============================================================================
// LOAD ORIGINAL QGEN-FRESH QUESTIONS
// ============================================================================

/**
 * Loads all questions from QGen-FRESH JSON files into a Map keyed by title.
 * Includes any question that has nested "blank N" options (TC, GI, etc.).
 */
function loadQGenTCQuestions(): Map<string, { options: any; answer: any }> {
    const map = new Map<string, { options: any; answer: any }>()

    // Collect all JSON file paths
    const filePaths: string[] = []

    // Root-level files
    const rootFiles = fs.readdirSync(QGEN_DIR)
        .filter(f => f.endsWith('.json') && !f.startsWith('.'))
        .map(f => path.join(QGEN_DIR, f))
    filePaths.push(...rootFiles)

    // Subdirectories (29-Dec, 30-Dec)
    const subdirs = fs.readdirSync(QGEN_DIR)
        .filter(d => fs.statSync(path.join(QGEN_DIR, d)).isDirectory())
    for (const subdir of subdirs) {
        const subdirPath = path.join(QGEN_DIR, subdir)
        const subFiles = fs.readdirSync(subdirPath)
            .filter(f => f.endsWith('.json'))
            .map(f => path.join(subdirPath, f))
        filePaths.push(...subFiles)
    }

    for (const filepath of filePaths) {
        const raw = fs.readFileSync(filepath, 'utf-8')
        let data: any
        try {
            data = JSON.parse(raw)
        } catch {
            continue
        }

        // Determine exam type from filename
        const filename = path.basename(filepath)
        const exam = filename.startsWith('GMAT') ? 'GMAT' : filename.startsWith('GRE') ? 'GRE' : null
        if (!exam) continue

        // Handle wrapper formats
        let sections: Record<string, any>
        if (data[exam]) {
            sections = data[exam]
        } else if (data['1'] || data['2'] || data['3'] || data['4']) {
            sections = data
        } else {
            continue
        }

        for (const [, sectionData] of Object.entries(sections)) {
            const sec = sectionData as any
            const questions = sec.questions || []

            for (const q of questions) {
                // Collect any question with nested blank options (TC, GI, etc.)
                if (q.options && q.title) {
                    const firstOptKey = Object.keys(q.options)[0]
                    const hasNestedBlanks = firstOptKey && firstOptKey.toLowerCase().startsWith('blank')
                    if (hasNestedBlanks) {
                        const title = q.title.substring(0, 200)
                        if (!map.has(title)) {
                            map.set(title, { options: q.options, answer: q.answer })
                        }
                    }
                }

                // Also check child questions
                if (q['child-questions']) {
                    for (const child of q['child-questions']) {
                        if (child.options && child.title) {
                            const firstChildKey = Object.keys(child.options)[0]
                            const hasNestedBlanks = firstChildKey && firstChildKey.toLowerCase().startsWith('blank')
                            if (hasNestedBlanks) {
                                const childTitle = child.title.substring(0, 200)
                                if (!map.has(childTitle)) {
                                    map.set(childTitle, { options: child.options, answer: child.answer })
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return map
}

// ============================================================================
// FIXED OPTIONS BUILDER (same logic as updated import-qgen-fresh.ts)
// ============================================================================

function determineCorrect(
    key: string,
    answer: string | string[] | number | Record<string, string> | null
): boolean {
    if (answer === null || answer === undefined) return false
    if (typeof answer === 'string') return key === answer
    if (Array.isArray(answer)) return answer.includes(key)
    return false
}

function buildOptions(
    options: Record<string, any> | null,
    answer: string | string[] | number | Record<string, string> | null
): { optiontext: string; iscorrect: boolean; group: string; explanation: string | null }[] {
    if (!options || options === null) return []

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
            const groupNumber = String(i + 1) // "1", "2", "3"

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

// ============================================================================
// MAIN REPAIR LOGIC
// ============================================================================

async function main() {
    console.log('=== TC Options Repair Script ===\n')

    // Test connection
    try {
        await prisma.$connect()
        console.log('DB connected:', process.env.DATABASE_URL?.split('@')[1] || 'unknown')
    } catch (err) {
        console.error('DB connection failed:', (err as Error).message)
        process.exit(1)
    }

    // Step 1: Load original QGen-FRESH TC questions
    console.log('\nLoading QGen-FRESH questions with nested blank options from JSON files...')
    const qgenMap = loadQGenTCQuestions()
    console.log(`Loaded ${qgenMap.size} unique questions with nested blanks from JSON files.`)

    // Step 2: Find broken TC questions in DB
    console.log('\nQuerying DB for TC questions with broken options...')
    const allProblems = await prisma.problems.findMany({
        where: {
            metadata: {
                path: ['generatedBy'],
                equals: 'QGen-FRESH-Import'
            }
        },
        include: {
            problemoptions: true
        }
    })

    // Filter to ANY questions with broken options (TC + GI both use nested blank structure)
    const broken = allProblems.filter(p => {
        return p.problemoptions.some(o => o.optiontext.includes('[object Object]'))
    })

    console.log(`Found ${broken.length} questions with broken options (TC + GI).`)

    if (broken.length === 0) {
        console.log('\nNo broken questions found. Nothing to fix.')
        return
    }

    // Step 3: Fix each broken question
    let fixed = 0
    let notFound = 0
    let errors = 0

    for (const problem of broken) {
        try {
            const original = qgenMap.get(problem.title)
            if (!original) {
                console.warn(`  SKIP: No original found for "${problem.title.substring(0, 60)}"`)
                notFound++
                continue
            }

            const newOptions = buildOptions(original.options, original.answer)
            if (newOptions.length === 0) {
                console.warn(`  SKIP: 0 options generated for "${problem.title.substring(0, 60)}"`)
                errors++
                continue
            }

            // Delete old broken options
            await prisma.problemoptions.deleteMany({
                where: { problemid: problem.problemid }
            })

            // Insert correct options
            await prisma.problemoptions.createMany({
                data: newOptions.map(opt => ({
                    problemid: problem.problemid,
                    optiontext: opt.optiontext,
                    iscorrect: opt.iscorrect,
                    group: opt.group,
                    explanation: opt.explanation
                }))
            })

            // Update options_type to "blank"
            await prisma.problems.update({
                where: { problemid: problem.problemid },
                data: { options_type: 'blank' }
            })

            fixed++
            console.log(`  FIXED: [${problem.problemid}] "${problem.title.substring(0, 50)}" (${newOptions.length} options)`)

        } catch (err) {
            console.error(`  ERROR: [${problem.problemid}] "${problem.title.substring(0, 50)}": ${(err as Error).message}`)
            errors++
        }
    }

    // Summary
    console.log('\n=== REPAIR SUMMARY ===')
    console.log(`  Fixed:     ${fixed}`)
    console.log(`  Not found: ${notFound}`)
    console.log(`  Errors:    ${errors}`)
    console.log(`  Total:     ${broken.length}`)
}

main()
    .then(async () => {
        await prisma.$disconnect()
        console.log('\nDone. DB disconnected.')
    })
    .catch(async (e) => {
        console.error('Fatal error:', e)
        await prisma.$disconnect()
        process.exit(1)
    })
