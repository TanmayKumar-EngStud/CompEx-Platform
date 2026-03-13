
import { QuestionGenerator } from '../automation/QuestionGenerator';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.production' });

async function main() {
    const qg = new QuestionGenerator();

    // Mock scope for Sentence Equivalence
    const scope = {
        examtypes: { name: 'GRE' },
        sections: { name: 'Verbal' },
        tags: { name: 'Sentence Equivalence' }
    };

    console.log("🧪 Testing Legacy Logic Restoration...");

    try {
        const question = await qg.generateChainedQuestion(scope, 2, 'verbal', 'TEST_LEGACY_1');

        console.log("\n✅ Generated Question:");
        console.log("Title:", question.title);
        console.log("Text:", question.text);
        console.log("Options Count:", question.options.length);
        console.log("First Option:", question.options[0]);
        console.log("Explanation Start:", question.explanation.substring(0, 100) + "...");

        // Assertions
        if (question.options.length !== 6) console.error("❌ FAILED: Sentence Equivalence must have 6 options.");
        else console.log("✅ Options Count Valid (6)");

        if (!question.text.includes("[BLANK]")) console.error("❌ FAILED: Missing [BLANK] in text.");
        else console.log("✅ Text Format Valid ([BLANK] present)");

        if (!question.explanation.includes("**Setup:**")) console.error("❌ FAILED: Missing '**Setup:**' in solution.");
        else console.log("✅ Solution Structure Valid (**Setup:** present)");

    } catch (error) {
        console.error("❌ Generation Error:", error);
    }
}

main();
