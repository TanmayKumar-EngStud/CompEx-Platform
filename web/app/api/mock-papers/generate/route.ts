// API Route: Generate Mock Paper with Balanced Question Distribution
// GET /api/mock-papers/generate

import { NextRequest, NextResponse } from 'next/server';
import { QuestionDistributionService, DEFAULT_CONFIG } from '@/features/question-distribution/question-distribution';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    
    // Parse distribution config from query params
    const config = {
      independentRatio: parseFloat(searchParams.get('independentRatio') || String(DEFAULT_CONFIG.independentRatio)),
      contextualRatio: parseFloat(searchParams.get('contextualRatio') || String(DEFAULT_CONFIG.contextualRatio)),
      easyRatio: parseFloat(searchParams.get('easyRatio') || String(DEFAULT_CONFIG.easyRatio)),
      mediumRatio: parseFloat(searchParams.get('mediumRatio') || String(DEFAULT_CONFIG.mediumRatio)),
      hardRatio: parseFloat(searchParams.get('hardRatio') || String(DEFAULT_CONFIG.hardRatio)),
      batchSize: parseInt(searchParams.get('batchSize') || String(DEFAULT_CONFIG.batchSize)),
      requireTopicCoverage: searchParams.get('requireTopicCoverage') === 'true',
      minTopicsRequired: parseInt(searchParams.get('minTopicsRequired') || '3'),
      minQualityScore: parseFloat(searchParams.get('minQualityScore') || String(DEFAULT_CONFIG.minQualityScore)),
    };
    
    // Generate mock paper
    const result = await QuestionDistributionService.generateMockPaper(config);
    
    return NextResponse.json({
      success: true,
      mockPaper: {
        questions: result.questions.map(q => ({
          id: q.problemid,
          title: q.title,
          type: q.type,
          difficulty: q.difficulty,
          topic: q.topicName,
          quality: q.qualityScore,
        })),
        distribution: result.distribution,
        source: result.source,
        remainingInBatch: result.remainingInBatch,
      },
      config: config,
      generatedAt: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('Error generating mock paper:', error);
    return NextResponse.json(
      { error: 'Failed to generate mock paper' },
      { status: 500 }
    );
  }
}
