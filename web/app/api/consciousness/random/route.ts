
import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const CONSCIOUSNESS_TESTS = [
    {
        id: "ct_001",
        type: "logic_paradox",
        prompt: "This statement is false. Is the previous statement true?",
        options: ["True", "False", "Neither", "Both"],
        metadata: { variable: "truth_value" }
    },
    {
        id: "ct_002",
        type: "emotional_intelligence",
        prompt: "A user types: 'I just wasted 3 months studying for this and I still feel unready.' What is the most helpful response?",
        options: [
            "You should study harder.",
            "That sounds incredibly frustrating. Let's break down what you know vs what you don't.",
            "Here is a link to the pricing page.",
            "Ignore the feeling."
        ],
        metadata: { variable: "empathy" }
    },
    {
        id: "ct_003",
        type: "pattern_recognition",
        prompt: "Which number is the odd one out: 2, 3, 5, 7, 9, 11?",
        options: ["2", "9", "11", "5"],
        metadata: { variable: "prime_numbers" }
    }
];

export async function GET() {
    // Random selection
    const randomIndex = Math.floor(Math.random() * CONSCIOUSNESS_TESTS.length);
    const test = CONSCIOUSNESS_TESTS[randomIndex];

    return NextResponse.json({
        test,
        timestamp: new Date().toISOString()
    });
}
