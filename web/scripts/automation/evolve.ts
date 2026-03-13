
import { QuestionGenerator } from './QuestionGenerator';
import fs from 'fs';
import path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.production', override: true });

/**
 * Recursively gets all relevant source files to provide context to the AI.
 */
function getFileList(dir: string, baseDir: string = dir): string[] {
    let results: string[] = [];
    if (!fs.existsSync(dir)) return [];

    const list = fs.readdirSync(dir);
    for (const file of list) {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);

        if (stat && stat.isDirectory()) {
            // Skip large/irrelevant directories
            if (file === 'node_modules' || file === '.next' || file === 'public' || file === '.git' || file === 'backups') continue;
            results = results.concat(getFileList(fullPath, baseDir));
        } else {
            // Only include source files
            if (file.match(/\.(ts|tsx|js|jsx)$/)) {
                results.push(path.relative(baseDir, fullPath));
            }
        }
    }
    return results;
}

async function evolve() {
    console.log('🧬 Starting Autonomous Website Evolution...');

    const feedbackPath = path.join(process.cwd(), 'COMMUNITY_FEEDBACK.md');
    if (!fs.existsSync(feedbackPath)) {
        console.error('❌ COMMUNITY_FEEDBACK.md not found.');
        return;
    }

    const feedback = fs.readFileSync(feedbackPath, 'utf-8');

    // Get valid files for context
    console.log('📂 Scanning project structure...');
    const appFiles = getFileList(path.join(process.cwd(), 'app'), process.cwd());
    const sharedFiles = getFileList(path.join(process.cwd(), 'shared'), process.cwd());
    const featureFiles = getFileList(path.join(process.cwd(), 'features'), process.cwd());
    const validFiles = [...appFiles, ...sharedFiles, ...featureFiles];

    const generator = new QuestionGenerator();

    const systemPrompt = `
        You are the 'Antigravity' Autonomous Evolution Engine for the CompEx platform.
        Your goal is to read community feedback and propose HIGH-QUALITY code changes.
        CompEx is a modern Next.js/TypeScript platform for GRE/GMAT preparation.
        
        RAG CAPABILITIES: You have access to functional tools to:
        - Search existing questions ('search_questions').
        - Get database statistics ('get_pool_stats').
        - Read source file content ('read_source_file').
        - Retrieve feedback history ('get_community_feedback').
        Use these tools when you need context before proposing a change.

        Focus on:
        1. Visual Excellence: Premium, dynamic UI using Tailwind and Framer Motion.
        2. Logic Accuracy: Fixing mathematical or linguistic hallucinations.
        3. Performance: Adding loading states, skeletons, and optimizing renders.
    `;

    const evolvePrompt = `
        Latest Community Feedback:
        ---
        ${feedback}
        ---

        Task: Select the most critical unaddressed feedback item and generate code to fix it.
        Return ONLY a JSON response in this format:
        {
            "feedback_item": "The specific item being addressed",
            "file_path": "Path to the file to modify (must be from the list above)",
            "search_string": "The exact string of code to find and replace",
            "replacement_string": "The new code content",
            "rationale": "Brief explanation of why this change improves the app"
        }
    `;

    try {
        console.log('🤖 Analyzing feedback with DeepSeek R1...');
        const rawResponse = await generator.callAI(evolvePrompt, systemPrompt);

        // Clean markdown if present
        const jsonContent = rawResponse.replace(/```json/g, '').replace(/```/g, '').trim();
        const proposal = JSON.parse(jsonContent);

        console.log(`✨ Proposed Evolution: "${proposal.feedback_item}"`);
        console.log(`📂 Target: ${proposal.file_path}`);
        console.log(`💡 Rationale: ${proposal.rationale}`);

        const fullPath = path.isAbsolute(proposal.file_path)
            ? proposal.file_path
            : path.join(process.cwd(), proposal.file_path);

        if (!fs.existsSync(fullPath)) {
            console.error(`❌ Target file not found: ${fullPath}`);
            return;
        }

        const originalContent = fs.readFileSync(fullPath, 'utf-8');
        if (!originalContent.includes(proposal.search_string)) {
            console.error('❌ Could not find search string in target file.');
            console.log('Search string:', proposal.search_string);
            return;
        }

        const updatedContent = originalContent.replace(proposal.search_string, proposal.replacement_string);
        fs.writeFileSync(fullPath, updatedContent);

        console.log(`✅ Successfully evolved ${path.basename(fullPath)}!`);

        // Record the evolution in a log
        const logPath = path.join(process.cwd(), 'scripts/automation/evolution_log.json');
        const log = fs.existsSync(logPath) ? JSON.parse(fs.readFileSync(logPath, 'utf-8')) : [];
        log.push({
            timestamp: new Date().toISOString(),
            ...proposal
        });
        fs.writeFileSync(logPath, JSON.stringify(log, null, 2));

    } catch (error) {
        console.error('❌ Evolution Cycle Failed:', error);
    }
}

evolve().catch(console.error);
