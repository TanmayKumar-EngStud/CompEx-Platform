
import { PrismaClient } from '@prisma/client';
import fs from 'fs';

const prisma = new PrismaClient();
const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'qwen2.5:7b'; // As seen in your logs

// Define the "Swarm" of Personas
const PERSONAS = [
    {
        id: 'rusher',
        name: 'The Rusher',
        system: "You are in a hurry. specific constraint: precise answer only. Solve this logic problem as fast as possible. Do not overthink.",
        options: { temperature: 0.8 }
    },
    {
        id: 'thinker',
        name: 'The Thinker',
        system: "You are a deep thinker. specific constraint: Chain-of-Thought required. Solve this logic problem step-by-step. Break down the premises before concluding.",
        options: { temperature: 0.2 }
    },
    {
        id: 'skeptic',
        name: 'The Skeptic',
        system: "You are a critical reviewer. Solve the problem, then critique your own reasoning to find potential flaws. Only then provide the final answer.",
        options: { temperature: 0.4 }
    }
];

async function queryOllama(prompt: string, system: string, options: any) {
    const start = Date.now();
    try {
        const res = await fetch(OLLAMA_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: MODEL,
                prompt,
                system,
                stream: false,
                options
            })
        });
        const data = await res.json();
        const duration = Date.now() - start;
        return {
            response: data.response,
            duration,
            eval_count: data.eval_count,
            eval_duration: data.eval_duration
        };
    } catch (e) {
        console.error("Ollama Error:", e);
        return null;
    }
}

async function main() {
    console.log('🧪 Starting AI Logic Benchmark...');
    console.log(`🤖 Model: ${MODEL}`);

    // 1. Fetch "Hard" Questions (Difficulty >= 3)
    const questions = await prisma.problems.findMany({
        where: {
            difficulty: { gte: 1 },
            // type: { contains: 'Reasoning', mode: 'insensitive' } // Optional filter
        },
        take: 2, // Run small batch first
        select: {
            problemid: true,
            text: true,
            difficulty: true,
            problemoptions: {
                where: { iscorrect: true },
                select: { optiontext: true }
            }
        }
    });

    // Let's re-check schema for answer. Usually in 'solution' json or 'problemoptions' table.
    // For this prototype, we'll just capture the output.

    console.log(`📚 Found ${questions.length} questions to benchmark.`);

    const results = [];

    for (const q of questions) {
        console.log(`\n🧩 Benchmarking Question ID: ${q.problemid} (Diff: ${q.difficulty})`);

        // Construct Prompt
        // If it's multiple choice, we need options.
        const options = await prisma.problemoptions.findMany({ where: { problemid: q.problemid } });
        let promptText = `Question: ${q.text}\n`;
        if (options.length > 0) {
            promptText += "Options:\n";
            options.forEach(o => promptText += `- ${o.optiontext}\n`);
        }

        for (const persona of PERSONAS) {
            process.stdout.write(`   Running Persona: ${persona.name}... `);

            const result = await queryOllama(promptText, persona.system, persona.options);

            if (result) {
                console.log(`✅ (${result.duration}ms)`);
                results.push({
                    questionId: q.problemid,
                    difficulty: q.difficulty,
                    persona: persona.id,
                    response: result.response,
                    metrics: {
                        total_duration_ms: result.duration,
                        tokens_eval: result.eval_count
                    },
                    timestamp: new Date()
                });
            } else {
                console.log(`❌ Failed`);
            }
        }
    }

    // Save Dataset
    const filename = `dataset_benchmark_${Date.now()}.json`;
    fs.writeFileSync(filename, JSON.stringify(results, null, 2));
    console.log(`\n💾 Dataset saved to ${filename}`);
    console.log('You can analyze this data for your paper!');
}

main()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
