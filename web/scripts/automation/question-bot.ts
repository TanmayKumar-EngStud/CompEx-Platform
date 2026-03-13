import { PrismaClient } from '@prisma/client'
import * as dotenv from 'dotenv'
import { QuestionGenerator } from './QuestionGenerator'

// Load environment variables
dotenv.config({ path: '.env.production', override: true })

const prisma = new PrismaClient({
    datasources: {
        db: {
            url: process.env.DATABASE_URL
        }
    }
})

const generator = new QuestionGenerator();

/**
 * Procedural Question Generator (Simulated AI)
 * Used as a robust fallback if OpenAI API fails or is unconfigured.
 */
class SimulatedAI {
    static generate(scope: any, difficulty: number) {
        const topic = scope.tags.name;
        const exam = scope.examtypes.name;

        // Templates based on topic
        const blueprints: Record<string, any[]> = {
            'Algebra': [
                {
                    title: "Linear Equation",
                    text: (v: any) => `If ${v.a}x + ${v.b} = ${v.c}, what is the value of x?`,
                    solve: (v: any) => (v.c - v.b) / v.a,
                    vars: () => ({ a: rand(1, 10), b: rand(1, 20), c: rand(20, 50) })
                },
                {
                    title: "Variable Relationship",
                    text: (v: any) => `If y = ${v.a}x + ${v.b} and x increases by ${v.i}, by how much does y increase?`,
                    solve: (v: any) => v.a * v.i,
                    vars: () => ({ a: rand(2, 8), b: rand(1, 15), i: rand(1, 5) })
                }
            ],
            'Geometry': [
                {
                    title: "Area of a Circle",
                    text: (v: any) => `
<div style="text-align: center; margin: 20px 0;">
  <svg width="100" height="100" viewBox="0 0 100 100" style="margin: auto; display: block;">
    <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="2" fill="none" />
    <line x1="50" y1="50" x2="90" y2="50" stroke="currentColor" stroke-width="2" />
    <text x="65" y="45" font-size="10" fill="currentColor">r = ${v.r}</text>
  </svg>
</div>
What is the area of a circle with a radius of ${v.r} units? (Keep in terms of π)`,
                    solve: (v: any) => `${v.r * v.r}π`,
                    vars: () => ({ r: rand(3, 15) })
                },
                {
                    title: "Triangle Hypotenuse",
                    text: (v: any) => `
<div style="text-align: center; margin: 20px 0;">
  <svg width="120" height="100" viewBox="0 0 120 100" style="margin: auto; display: block;">
    <path d="M 20 80 L 100 80 L 20 20 Z" stroke="currentColor" stroke-width="2" fill="none" />
    <rect x="20" y="70" width="10" height="10" stroke="currentColor" stroke-width="1" fill="none" />
    <text x="55" y="95" font-size="10" fill="currentColor">base = ${v.b}</text>
    <text x="0" y="55" font-size="10" fill="currentColor">ht = ${v.a}</text>
    <text x="65" y="45" font-size="10" fill="currentColor">x = ?</text>
  </svg>
</div>
In the right triangle shown above, find the value of x if the altitude is ${v.a} and the base is ${v.b}.`,
                    solve: (v: any) => Math.sqrt(v.a * v.a + v.b * v.b).toFixed(2),
                    vars: () => {
                        const pairs = [[3, 4], [5, 12], [8, 15], [7, 24]];
                        const p = pairs[rand(0, 3)];
                        const scale = rand(1, 3);
                        return { a: p[0] * scale, b: p[1] * scale };
                    }
                },
                {
                    title: "Square Perimeter",
                    text: (v: any) => `
<div style="text-align: center; margin: 20px 0;">
  <svg width="100" height="100" viewBox="0 0 100 100" style="margin: auto; display: block;">
    <rect x="20" y="20" width="60" height="60" stroke="currentColor" stroke-width="2" fill="none" />
    <text x="45" y="15" font-size="10" fill="currentColor">s = ${v.s}</text>
  </svg>
</div>
If each side of a square is ${v.s} units, what is its perimeter?`,
                    solve: (v: any) => v.s * 4,
                    vars: () => ({ s: rand(4, 25) })
                }
            ],
            'Reading Comprehension': [
                {
                    title: "Main Idea",
                    text: (v: any) => `Passage: <br/><blockquote style="border-left: 4px solid #ccc; padding-left: 10px;">${v.p}</blockquote><br/>What is the primary purpose of the author in the passage above?`,
                    solve: (v: any) => v.ans,
                    vars: () => ({
                        p: "The recent discovery of bioluminescent fungi in the Amazon basin has challenged previous assumptions about the distribution of light-emitting organisms. Researchers are currently examining the evolutionary advantages of such traits in dense forest environments.",
                        ans: "To describe a recent scientific discovery and its implications for evolutionary biology."
                    })
                }
            ],
            'Arithmetic': [
                {
                    title: "Prime Factorization",
                    text: (v: any) => `How many distinct prime factors does the number ${v.n} have?`,
                    solve: (v: any) => v.ans,
                    vars: () => {
                        const pairs = [[24, 2], [30, 3], [60, 3], [105, 3], [210, 4]];
                        const p = pairs[rand(0, 4)];
                        return { n: p[0], ans: p[1] };
                    }
                }
            ]
        };

        const defaultBlueprints = [
            {
                title: `${topic} Challenge`,
                text: () => `Identify the correct property of ${topic} as it relates to ${exam} standards.`,
                solve: () => "Consult standard practice materials for the detailed proof.",
                vars: () => ({})
            }
        ];

        const topicBlueprints = blueprints[topic] || defaultBlueprints;
        const bp = topicBlueprints[rand(0, topicBlueprints.length - 1)];
        const v = bp.vars();
        const solution = bp.solve(v);

        return {
            title: bp.title,
            text: bp.text(v),
            options: [
                { text: String(solution), isCorrect: true },
                { text: String(Number(solution) + rand(1, 5) || "None of the above"), isCorrect: false },
                { text: String(Number(solution) - rand(1, 5) || "It cannot be determined"), isCorrect: false },
                { text: String(Number(solution) * 2 || "All of the above"), isCorrect: false }
            ],
            explanation: `The solution is derived by applying ${topic} principles. Final answer: ${solution}.`
        };
    }
}

function rand(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}



async function generateAndInsertQuestion() {
    try {
        console.log('\n🔍 Fetching available categories...')
        console.log(`📡 Connecting to: ${process.env.DATABASE_URL?.split('@')[1]}`)

        const scopes = await prisma.tag_scopes.findMany({
            include: {
                tags: true,
                examtypes: true,
                sections: true
            }
        })

        console.log(`📊 Found ${scopes.length} tag scopes.`)

        if (scopes.length === 0) {
            console.warn('⚠️ No tag scopes found. Please run seeding first.')
            return
        }

        // Randomly pick a scope
        const scope = scopes[Math.floor(Math.random() * scopes.length)]
        const difficulty = Math.floor(Math.random() * 5) + 1 // 1-5

        let data;
        try {
            // Use Chained Generation for Quants AND Verbal topics (DeepSeek Optimized)
            const isQuants = scope.sections.name.toLowerCase().includes('quant') || scope.tags.name === 'Algebra' || scope.tags.name === 'Arithmetic' || scope.tags.name === 'Geometry';
            const isVerbal = scope.sections.name.toLowerCase().includes('verbal') || scope.tags.name.includes('Reading') || scope.tags.name.includes('Text') || scope.tags.name.includes('Critical');

            if (isQuants || isVerbal) {
                // Determine template prefix based on section
                const templatePrefix = isQuants ? 'quants' : 'verbal';
                data = await generator.generateChainedQuestion(scope, difficulty, templatePrefix);
            } else {
                console.log(`🤖 Requesting Monolithic AI for: ${scope.tags.name}...`)
                const prompt = `
                    You are an expert ${scope.examtypes.name} question writer.
                    ...
                `; // (Existing monolithic prompt logic)
                // For brevity, I'll keep the monolithic fallback simple or just use the new one for everything if I had templates
                // But for now, I only have Quants templates.

                // Let's just use the existing monolithic logic for non-quants
                const monolithicPrompt = `
                    You are an expert ${scope.examtypes.name} question writer for the actual official exam. 
                    Difficulty Level: ${difficulty}/5.
                    Topic: ${scope.tags.name}.
                    Return JSON: { title, text, options: [{text, isCorrect}], explanation }
                `;
                const content = await generator.callAI(monolithicPrompt);
                data = JSON.parse(content.replace(/```json/g, '').replace(/```/g, '').trim());
            }
        } catch (e) {
            console.error('⚠️ AI Cycle Error:', e);
            console.log('🔮 Using Procedural Generation (AI Fallback)...')
            data = SimulatedAI.generate(scope, difficulty);
        }

        // Insert into database
        const problem = await prisma.problems.create({
            data: {
                title: data.title || `${scope.tags.name} Problem`,
                text: data.text || "Problem content missing.",
                difficulty: difficulty,
                sectionid: scope.sectionid,
                examtypeid: scope.examtypeid,
                isMockQuestion: false,
                type: 'Multiple Choice',
                addedDate: new Date(),
                metadata: {
                    generatedBy: 'Bot Swarm',
                    topic: scope.tags.name,
                    explanation: data.explanation
                },
                problemoptions: {
                    create: (data.options || []).map((opt: any, idx: number) => ({
                        optiontext: opt.text || "Option",
                        iscorrect: !!opt.isCorrect,
                        group: String.fromCharCode(65 + idx)
                    }))
                }
            }
        })

        // Link to tag scope
        await prisma.problemtags.create({
            data: {
                problemid: problem.problemid,
                tagScopeId: scope.tagScopeId
            }
        })

        console.log(`✅ [${new Date().toLocaleTimeString()}] Created problem ID: ${problem.problemid} ("${data.title}")`)

    } catch (error) {
        console.error('❌ Cycle Error:', error)
    }
}

async function startBot() {
    console.log('🚀 Question Generation Bot Started')
    console.log('⏱️ Interval: 15 seconds')

    // Run immediately
    await generateAndInsertQuestion()

    // Then loop
    setInterval(async () => {
        await generateAndInsertQuestion()
    }, 15000)
}

startBot().catch(console.error)
