
import { PrismaClient } from '@prisma/client'
import OpenAI from 'openai'
import * as dotenv from 'dotenv'
import { TemplateEngine } from './TemplateEngine'
import { PhaseCache } from './PhaseCache'
import { DeepSeekToolkit, DEEPSEEK_TOOLS } from './DeepSeekToolkit'

// Load environment variables
dotenv.config({ path: '.env.production', override: true })

export class QuestionGenerator {
    private engine: TemplateEngine;
    private cache: PhaseCache;
    private openai: OpenAI;
    private deepseek: OpenAI | null = null;
    private toolkit: DeepSeekToolkit;
    private geminiKeys: string[] = [];
    private currentGeminiKeyIndex = 0;

    constructor() {
        this.engine = new TemplateEngine();
        this.cache = new PhaseCache();
        this.toolkit = new DeepSeekToolkit();

        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY || 'N/A'
        });

        if (process.env.DEEPSEEK_API_KEY) {
            this.deepseek = new OpenAI({
                apiKey: process.env.DEEPSEEK_API_KEY,
                baseURL: 'https://api.deepseek.com'
            });
        }

        this.geminiKeys = (process.env.GOOGLE_AI_STUDIO_KEYS || process.env.GOOGLE_AI_STUDIO_KEY || '').split(',').map(k => k.trim()).filter(Boolean);
    }

    public async callAI(prompt: string, systemPrompt?: string): Promise<string> {
        // Use RAG-enabled chat if possible for reasoning/evolution tasks
        if (this.deepseek && (prompt.toLowerCase().includes('evolve') || prompt.toLowerCase().includes('feedback') || prompt.toLowerCase().includes('structure'))) {
            try {
                return await this.callAIWithTools(prompt, systemPrompt);
            } catch (e) {
                console.warn('⚠️ DeepSeek Tool Call Failed, falling back to R1...', (e as any).message);
            }
        }

        // 1. Priority: DeepSeek R1 (Reasoning)
        if (this.deepseek) {
            try {
                const response = await this.deepseek.chat.completions.create({
                    model: "deepseek-reasoner",
                    messages: [
                        {
                            role: "user", content: (systemPrompt ? systemPrompt + "\n\n" : "") +
                                "IMPORTANT: Return ONLY valid JSON. Do not include any conversational text, markdown formatting like ```json, or explanations outside the JSON object.\n\n" + prompt
                        }
                    ],
                }, { timeout: 90000 });
                const content = response.choices[0].message.content || "";
                return content.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
            } catch (e: any) {
                console.warn('⚠️ DeepSeek R1 Failed:', e.message);
            }
        }

        // ... fallback to Gemini/OpenAI
        return this.fallbackAI(prompt, systemPrompt);
    }

    private async callAIWithTools(prompt: string, systemPrompt?: string, recursionDepth = 0): Promise<string> {
        if (!this.deepseek) throw new Error('DeepSeek client not available');
        if (recursionDepth > 5) throw new Error('AI Tool recursion depth exceeded');

        const messages: any[] = [
            ...(systemPrompt ? [{ role: "system", content: systemPrompt }] : []),
            { role: "user", content: prompt }
        ];

        console.log(`🤖 DeepSeek RAG Cycle [Depth: ${recursionDepth}]...`);

        const response = await this.deepseek.chat.completions.create({
            model: "deepseek-chat",
            messages,
            tools: DEEPSEEK_TOOLS as any,
            tool_choice: "auto"
        });

        const message = response.choices[0].message;

        if (message.tool_calls && message.tool_calls.length > 0) {
            const toolResults = [];
            for (const toolCall of message.tool_calls as any[]) {
                const result = await this.toolkit.executeTool(toolCall.function.name, JSON.parse(toolCall.function.arguments));
                toolResults.push({
                    role: "tool",
                    tool_call_id: toolCall.id,
                    content: result
                });
            }

            // Recursively call AI with tool results
            const secondPrompt = `Here are the tool results for your previous query:\n${JSON.stringify(toolResults)}\n\nNow, finalize your response. Return ONLY valid JSON.`;
            return this.callAIWithTools(secondPrompt, systemPrompt, recursionDepth + 1);
        }

        const content = (message.content || "").trim();
        return content.replace(/```json/g, '').replace(/```/g, '').trim();
    }

    private async fallbackAI(prompt: string, systemPrompt?: string): Promise<string> {
        // 1. Gemini Rotation (Fallback)
        if (this.geminiKeys.length > 0) {
            for (let i = 0; i < this.geminiKeys.length; i++) {
                const key = this.geminiKeys[this.currentGeminiKeyIndex];
                try {
                    return await this.generateWithGemini(prompt, key, systemPrompt);
                } catch (e: any) {
                    if (e.message.includes('RESOURCE_EXHAUSTED')) {
                        console.warn(`⚠️ Gemini Key ${this.currentGeminiKeyIndex + 1} exhausted. Rotating...`);
                        this.currentGeminiKeyIndex = (this.currentGeminiKeyIndex + 1) % this.geminiKeys.length;
                        continue;
                    }
                    console.warn(`⚠️ Gemini Key ${this.currentGeminiKeyIndex + 1} failed:`, e.message);
                    break;
                }
            }
        }

        // 2. OpenAI Fallback
        if (process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY !== 'N/A') {
            try {
                const response = await this.openai.chat.completions.create({
                    model: "gpt-4o-mini", // Fallback model
                    messages: [
                        ...(systemPrompt ? [{ role: "system" as const, content: systemPrompt }] : []),
                        { role: "user" as const, content: prompt }
                    ],
                    response_format: { type: "json_object" },
                }, { timeout: 15000 });
                return response.choices[0].message.content || "";
            } catch (e: any) {
                console.warn('⚠️ OpenAI Failed:', e.message);
            }
        }

        throw new Error('All AI Providers (DeepSeek/Gemini/OpenAI) failed.');
    }

    private async generateWithGemini(prompt: string, apiKey: string, systemPrompt?: string) {
        // console.log('💎 Using Gemini 1.5 Flash (Free Tier)...')
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
        try {
            const body: any = {
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { responseMimeType: "application/json" }
            };
            if (systemPrompt) {
                body.system_instruction = { parts: [{ text: systemPrompt }] };
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const err = await response.text();
                throw new Error(`Gemini API error: ${response.status} - ${err}`);
            }
            const data: any = await response.json();
            return data.candidates[0].content.parts[0].text;
        } catch (e) {
            console.error('❌ Gemini Error:', e);
            throw e;
        }
    }

    public async generateChainedQuestion(scope: any, difficulty: number, templatePrefix: 'quants' | 'verbal', variation: string = '1') {
        const chainId = Math.random().toString(36).substring(7);
        console.log(`[${chainId}] 🏗️  Starting Chained Generation: ${scope.tags.name} (${templatePrefix.toUpperCase()}) - Diff: ${difficulty} [Var: ${variation}]`);

        const systemTemplateName = templatePrefix === 'quants' ? 'quants-generic' : 'verbal-generic';
        const systemPrompt = this.engine.getSystemTemplate(systemTemplateName);
        const scopeId = `${scope.examtypes.name}-${scope.sections.name}-${scope.tags.name}`.replace(/[^a-zA-Z0-9]/g, '-');

        try {
            // Step 1: Metadata
            // We append variation to cache key to ensure we don't return the same cached metadata for different variations
            let metadata = this.cache.get(scopeId, difficulty, `metadata_v${variation}`);
            if (!metadata) {
                const metadataPrompt = this.engine.render(this.engine.getComponentTemplate(`${templatePrefix}-metadata`), {
                    exam_type: scope.examtypes.name,
                    section_name: scope.sections.name,
                    difficulty: difficulty,
                    requested_topic: scope.tags.name // Inject requested topic
                }) + `\n\n[VARIATION SEED: ${variation}] (Ensure this question is unique and distinct from previous variations)`; // Inject variation hint

                const metadataRaw = await this.callAI(metadataPrompt, systemPrompt);
                const parsed = JSON.parse(metadataRaw);

                // Handle One-Shot Generation (DeepSeek Shortcut)
                if (parsed.metadata && parsed.text && parsed.options) {
                    console.log(`[${chainId}] ⚡️ DeepSeek generated full question in one shot!`);
                    metadata = parsed.metadata;
                    // Populate cache for subsequent steps to 'find'
                    this.cache.set(scopeId, difficulty, `metadata_v${variation}`, metadata);
                    // Normalize text: Replace ______ with [BLANK]
                    const normalizedText = parsed.text.replace(/_+/g, '[BLANK]');
                    this.cache.set(scopeId, difficulty, `text_v${variation}`, { question_text: normalizedText });

                    // Normalize options
                    const optsObj: any = {};
                    parsed.options.forEach((opt: string) => {
                        // Extract letter and text e.g. "A) word" -> key="A", val="word"
                        const match = opt.match(/^([A-F])[\)\.]\s*(.+)$/);
                        if (match) {
                            optsObj[match[1]] = { text: match[2], explanation: parsed.solution?.key_vocabulary?.[match[2]] || "See solution." };
                        } else {
                            // Fallback if no letter prefix
                            const letter = String.fromCharCode(65 + Object.keys(optsObj).length);
                            optsObj[letter] = { text: opt, explanation: "See solution." };
                        }
                    });

                    this.cache.set(scopeId, difficulty, `options_v${variation}`, {
                        options: optsObj,
                        answer: parsed.solution.correct_answers || parsed.solution.answer,
                        explanations: {}
                    });

                    // We intentionally DO NOT cache solution_v here.
                    // This forces Step 4 to run, using the strict 'verbal-solution' template.
                } else if (parsed.metadata) {
                    // Nested metadata case
                    metadata = parsed.metadata;
                    this.cache.set(scopeId, difficulty, `metadata_v${variation}`, metadata);
                } else {
                    // Standard case
                    metadata = parsed;
                    this.cache.set(scopeId, difficulty, `metadata_v${variation}`, metadata);
                }
            }

            // Step 2: Question Text
            // console.log(`[${chainId}]    ↳ Phase 2: Question Text...`);
            let textData = this.cache.get(scopeId, difficulty, `text_v${variation}`);
            if (!textData) {
                const textPrompt = this.engine.render(this.engine.getComponentTemplate(`${templatePrefix}-text`), {
                    exam_type: scope.examtypes.name,
                    section_name: scope.sections.name,
                    topic: metadata.topic,
                    difficulty: difficulty,
                    scenario: metadata.theme
                });
                const textRaw = await this.callAI(textPrompt, systemPrompt);
                console.log(`[DEBUG] Text Raw:`, textRaw); // DEBUG
                textData = JSON.parse(textRaw);
                this.cache.set(scopeId, difficulty, `text_v${variation}`, textData);
            }

            // Step 3: Options & Answer
            let optionsData = this.cache.get(scopeId, difficulty, `options_v${variation}`);
            if (!optionsData) {
                const optionsPrompt = this.engine.render(this.engine.getComponentTemplate(`${templatePrefix}-options`), {
                    exam_type: scope.examtypes.name,
                    section_name: scope.sections.name,
                    question_text: textData.question_text
                });
                const optionsRaw = await this.callAI(optionsPrompt, systemPrompt);
                optionsData = JSON.parse(optionsRaw);
                this.cache.set(scopeId, difficulty, `options_v${variation}`, optionsData);
            }

            // Step 4: Solution
            let solutionData = this.cache.get(scopeId, difficulty, `solution_v${variation}`);
            if (!solutionData) {
                const solutionPrompt = this.engine.render(this.engine.getComponentTemplate(`${templatePrefix}-solution`), {
                    exam_type: scope.examtypes.name,
                    question_text: textData.question_text,
                    options: optionsData.options,
                    answer: optionsData.answer
                });
                const solutionRaw = await this.callAI(solutionPrompt, systemPrompt);
                solutionData = JSON.parse(solutionRaw);
                this.cache.set(scopeId, difficulty, `solution_v${variation}`, solutionData);
            }

            // Clear cache after successful completion (Only for this variation)
            // Actually, we might want to keep it if we retry, but "resumable" means we clear valid runs
            // To be safe and clean, we remove specific variation keys
            this.cache.set(scopeId, difficulty, `metadata_v${variation}`, null); // Soft remove or implement delete in Cache
            // For now, let's just leave it or explicit clear. 
            // PhaseCache assumes 'clear' wipes all phases. Let's update PhaseCache later if needed.
            // For now simplest is to just not wipe, let them expire, OR add a specific clear.

            console.log(`[${chainId}] ✅ Generated: "${metadata.topic}"`);

            return {
                title: metadata.topic,
                text: textData.question_text,
                options: Object.entries(optionsData.options).map(([key, val]) => {
                    const optionText = typeof val === 'object' && val !== null ? (val as any).text : val;
                    const explanation = typeof val === 'object' && val !== null ? (val as any).explanation : undefined;

                    const isCorrect = Array.isArray(optionsData.answer)
                        ? optionsData.answer.includes(key)
                        : key === optionsData.answer;

                    return {
                        text: optionText,
                        isCorrect: isCorrect,
                        explanation: explanation
                    };
                }),
                explanation: solutionData.solution,
                metadata: {
                    ...metadata,
                    explanations: optionsData.explanations || Object.entries(optionsData.options).reduce((acc: any, [key, val]: any) => {
                        if (typeof val === 'object' && val.explanation) {
                            acc[key] = val.explanation;
                        }
                        return acc;
                    }, {})
                }
            };

        } catch (error) {
            console.error(`[${chainId}] ❌ Generation Failed:`, error);
            throw error; // Let caller handle or retry
        }
    }
}
