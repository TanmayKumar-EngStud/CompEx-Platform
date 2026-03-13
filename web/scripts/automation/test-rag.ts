
import { QuestionGenerator } from './QuestionGenerator';

async function testRAG() {
    console.log('🧪 Testing DeepSeek RAG Functional Toolkit...');

    const generator = new QuestionGenerator();

    const testPrompt = `
        Task: Analyze the current question pool distribution and identify gaps.
        Then, read the file 'app/verify/page.tsx' to understand how we currently present the question pool statistics.
        Based on this, suggest a new feedback item for the evolution engine.
    `;

    const systemPrompt = `
        You are an AI auditor for the CompEx platform.
        You have access to RAG tools to investigate the codebase and database.
    `;

    try {
        console.log('🤔 Asking AI to investigate (this should trigger multiple tool calls)...');
        const response = await generator.callAI(testPrompt, systemPrompt);

        console.log('\n✨ AI Response:');
        console.log('-------------------');
        console.log(response);
        console.log('-------------------');
        console.log('✅ RAG Verification Complete.');
    } catch (error) {
        console.error('❌ RAG Verification Failed:', error);
    }
}

testRAG().catch(console.error);
