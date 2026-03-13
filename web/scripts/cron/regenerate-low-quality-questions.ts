// Weekly cron job to regenerate low-quality questions
// Run this with: npx ts-node scripts/cron/regenerate-low-quality-questions.ts

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function regenerateLowQualityQuestions() {
    console.log('🔍 Starting quality check...');

    // Find questions with quality score below threshold
    const lowQualityQuestions = await prisma.questionQualityMetrics.findMany({
        where: {
            qualityScore: {
                lt: 5.0 // Quality below 5.0 needs regeneration
            },
            ratingCount: {
                gte: 3 // At least 3 ratings to be confident
            }
        },
        orderBy: {
            qualityScore: 'asc'
        },
        take: 10 // Process 10 questions at a time
    });

    console.log(`Found ${lowQualityQuestions.length} questions to review`);

    for (const metric of lowQualityQuestions) {
        console.log(`\n📝 Processing question ${metric.questionId}...`);
        console.log(`   Quality Score: ${metric.qualityScore.toFixed(2)}`);
        console.log(`   Average Rating: ${metric.avgRating.toFixed(2)}`);
        console.log(`   Variance: ${metric.variance.toFixed(2)}`);

        // Get the original question
        const question = await prisma.problems.findUnique({
            where: { problemid: metric.questionId }
        });

        if (!question) {
            console.log(`   ❌ Question not found, marking for review`);
            continue;
        }

        // Generate replacement using Antigravity
        const prompt = `
            You are an expert GRE/GMAT question writer.
            
            Create a new practice question based on this context:
            - Type: ${question.type}
            - Difficulty: ${question.difficulty}/5
            - Topic tags: ${JSON.stringify((question.metadata as any)?.tags || [])}
            - Previous question title: ${question.title}
            - Previous question text: ${question.text}
            
            Requirements:
            1. Create a unique question that tests the same concept
            2. Make it similar difficulty level
            3. Ensure the question is clear and has one correct answer
            4. Include brief explanation for the correct answer
            5. Make it engaging and relevant to test-takers
            
            Return the new question in this format:
            {
              "title": "Brief descriptive title",
              "text": "The full question text",
              "difficulty": ${question.difficulty},
              "options": [
                {"optiontext": "Option A", "iscorrect": true},
                {"optiontext": "Option B", "iscorrect": false},
                {"optiontext": "Option C", "iscorrect": false},
                {"optiontext": "Option D", "iscorrect": false}
              ],
              "explanation": "Brief explanation of why the correct answer is right"
            }
        `;

        try {
            // Call Antigravity API
            const aiResponse = await fetch('https://api.antigravity.com/v1/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${process.env.ANTIGRAVITY_API_KEY}`
                },
                body: JSON.stringify({
                    prompt,
                    model: 'reasoning',
                    max_tokens: 2000
                })
            });

            let newQuestionData = null;
            if (aiResponse.ok) {
                const aiResult = await aiResponse.json();
                try {
                    newQuestionData = JSON.parse(aiResult.text || aiResult.content);
                } catch (e) {
                    console.log('   ⚠️ Failed to parse AI response');
                }
            }

            // Option 1: Mark as needs review (human review required)
            await prisma.problems.update({
                where: { problemid: metric.questionId },
                data: {
                    metadata: {
                        ...(question.metadata as object || {}),
                        needsReview: true,
                        reviewReason: `Low quality score: ${metric.qualityScore.toFixed(2)}`,
                        reviewedAt: null
                    }
                }
            });

            console.log(`   ✅ Question marked for review`);

            // Option 2: If AI response was successful, queue for approval
            if (newQuestionData) {
                // Store new question in a staging table or queue for manual review
                console.log(`   🤖 AI generated replacement (needs review)`);
            }

        } catch (error) {
            console.error(`   ❌ Error processing question:`, error);
        }
    }

    console.log('\n✨ Quality check complete!');
    console.log(`${lowQualityQuestions.length} questions need review.`);
}

// Run the cron job
regenerateLowQualityQuestions()
    .catch(console.error)
    .finally(async () => {
        await prisma.$disconnect();
    });

// Export for use in cron jobs
export { regenerateLowQualityQuestions };
