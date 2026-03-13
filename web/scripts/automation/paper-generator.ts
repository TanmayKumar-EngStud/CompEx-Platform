
import { PrismaClient } from '@prisma/client'
import * as dotenv from 'dotenv'
import { QuestionGenerator } from './QuestionGenerator'
import { Command } from 'commander'

dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: { db: { url: process.env.DATABASE_URL } }
})

const generator = new QuestionGenerator();

async function getScopesForExam(examName: string) {
    return await prisma.tag_scopes.findMany({
        where: {
            examtypes: { name: { contains: examName, mode: 'insensitive' } }
        },
        include: { tags: true, examtypes: true, sections: true }
    });
}

async function generateSingleQuestion(scope: any, difficulty: number, isMock: boolean, variation: string) {
    try {
        const isQuants = scope.sections.name.toLowerCase().includes('quant') ||
            ['Algebra', 'Arithmetic', 'Geometry'].includes(scope.tags.name);

        // Default to Quants if unknown, or Verbal if explicitly verbal
        const templatePrefix = (isQuants) ? 'quants' : 'verbal';

        // Generate content
        const data = await generator.generateChainedQuestion(scope, difficulty, templatePrefix, variation);

        // Insert into DB
        const problem = await prisma.problems.create({
            data: {
                title: data.title || `${scope.tags.name} Problem`,
                text: data.text || "Problem content missing.",
                difficulty: difficulty,
                sectionid: scope.sectionid,
                examtypeid: scope.examtypeid,
                isMockQuestion: isMock, // Logic Flag
                type: 'Multiple Choice',
                addedDate: new Date(),
                metadata: {
                    generatedBy: 'DeepSeek Parallel Batch',
                    topic: scope.tags.name,
                    explanation: data.explanation,
                    ...data.metadata
                },
                problemoptions: {
                    create: (data.options || []).map((opt: any, idx: number) => ({
                        optiontext: opt.text || "Option",
                        iscorrect: !!opt.isCorrect,
                        group: String.fromCharCode(65 + idx)
                    }))
                }
            }
        });

        // Link tag
        await prisma.problemtags.create({
            data: { problemid: problem.problemid, tagScopeId: scope.tagScopeId }
        });

        console.log(`✅ [${isMock ? 'MOCK' : 'PRACTICE'}] Generated ID: ${problem.problemid} (${scope.tags.name} - L${difficulty})`);
        return true;
    } catch (error) {
        console.error(`❌ Failed generation for ${scope.tags.name}:`, error);
        return false;
    }
}


async function performAutonomousMaintenance(threshold: number = 4.5) {
    console.log(`\n♻️  Starting Autonomous Maintenance (Threshold: ${threshold}/10)...`);

    // 1. Find garbage questions (active and quality < threshold)
    const garbageMetrics = await prisma.questionQualityMetrics.findMany({
        where: {
            qualityScore: { lt: threshold }
        }
    });

    if (garbageMetrics.length === 0) {
        console.log('✅ No garbage questions detected.');
        return;
    }

    const garbageIds = garbageMetrics.map(m => m.questionId);

    // 2. Fetch garbage questions with their mock status and tags
    const garbageQuestions = await prisma.problems.findMany({
        where: {
            problemid: { in: garbageIds },
            isActive: true
        }
    });

    console.log(`📦 Identified ${garbageQuestions.length} active garbage questions.`);

    for (const question of garbageQuestions) {
        console.log(`   - Deactivating Question ID: ${question.problemid} (Mock: ${question.isMockQuestion})`);

        // Deactivate
        await prisma.problems.update({
            where: { problemid: question.problemid },
            data: { isActive: false }
        });

        // 3. If it was a mock question, we need to replace it to keep the mock paper fresh
        if (question.isMockQuestion) {
            // Find the tag scope for this question
            const tagLink = await prisma.problemtags.findFirst({
                where: { problemid: question.problemid }
            });

            if (tagLink) {
                // Find a high-quality practice question (isMock: false) in the same scope
                const replacement = await prisma.problems.findFirst({
                    where: {
                        isActive: true,
                        isMockQuestion: false,
                        problemtags: {
                            some: { tagScopeId: tagLink.tagScopeId }
                        },
                        QuestionQualityMetrics: {
                            qualityScore: { gte: threshold }
                        }
                    },
                    orderBy: {
                        popularityIndex: 'desc'
                    }
                });

                if (replacement) {
                    console.log(`   ✨ Found Replacement! Promoting Practice Question ID: ${replacement.problemid} to MOCK.`);
                    await prisma.problems.update({
                        where: { problemid: replacement.problemid },
                        data: { isMockQuestion: true }
                    });
                } else {
                    console.warn(`   ⚠️ No high-quality replacement found for scope ${tagLink.tagScopeId}.`);
                }
            }
        }
    }

    console.log('✨ Maintenance Cycle Complete.\n');
}

async function runBatch(options: {
    exam: string,
    count: number,
    concurrency: number,
    mock: boolean,
    startDifficulty: number,
    autoCleanup?: boolean
}) {
    if (options.autoCleanup) {
        await performAutonomousMaintenance();
    }

    console.log(`🚀 Starting Batch Generation: ${options.count} questions for ${options.exam}`);
    console.log(`⚙️  Concurrency: ${options.concurrency} | Mode: ${options.mock ? 'MOCK Exam' : 'Practice Bank'}`);

    let scopes = await getScopesForExam(options.exam);
    if (scopes.length === 0) {
        console.error(`❌ No scopes found for exam: ${options.exam}`);
        return;
    }

    // Shuffle Scopes (Fisher-Yates) for better distribution
    for (let i = scopes.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [scopes[i], scopes[j]] = [scopes[j], scopes[i]];
    }
    console.log(`🔀 Scopes Shuffled (Count: ${scopes.length})`);

    const tasks = [];

    for (let i = 0; i < options.count; i++) {
        // Round-robin from shuffled list
        const scope = scopes[i % scopes.length];

        // Generate a unique variation seed for this specific question instance
        // This allows generating multiple unique questions for the same topic (if loop wraps around)
        const variationSeed = `Batch-${Date.now()}-${i}`;

        tasks.push(() => generateSingleQuestion(scope, options.startDifficulty, options.mock, variationSeed));
    }

    // Execute with concurrency limit
    for (let i = 0; i < tasks.length; i += options.concurrency) {
        const chunk = tasks.slice(i, i + options.concurrency);
        await Promise.all(chunk.map(fn => fn()));
    }

    console.log('✨ Batch Complete.');
}

// CLI Setup
const program = new Command();

program
    .option('-e, --exam <type>', 'Exam name (GRE, GMAT)', 'GMAT')
    .option('-c, --count <number>', 'Total questions to generate', '10')
    .option('-p, --parallel <number>', 'Concurrency limit', '5')
    .option('-m, --mock <boolean>', 'Is this a Mock Exam batch? (true/false)', 'false')
    .option('-d, --difficulty <number>', 'Difficulty Level (1-5)', '3')
    .option('--cleanup', 'Run autonomous garbage collection before generation', true)
    .parse(process.argv);

const opts = program.opts();

runBatch({
    exam: opts.exam,
    count: parseInt(opts.count),
    concurrency: parseInt(opts.parallel),
    mock: opts.mock === 'true',
    startDifficulty: parseInt(opts.difficulty),
    autoCleanup: opts.cleanup !== false
}).catch(console.error);
