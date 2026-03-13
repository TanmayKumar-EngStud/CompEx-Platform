// API Route: Add New Question Batch
// POST /api/questions/batch/add

import { NextRequest, NextResponse } from 'next/server';
import { QuestionDistributionService, QuestionType } from '@/features/question-distribution/question-distribution';

interface QuestionBatchItem {
  title: string;
  text: string;
  type: 'independent' | 'contextual';
  difficulty: number; // 0-3
  sectionId: number;
  examTypeId: number;
  options: {
    text: string;
    isCorrect: boolean;
  }[];
  solution?: string;
  metadata?: Record<string, any>;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { questions, sectionId, examTypeId } = body as {
      questions: QuestionBatchItem[];
      sectionId?: number;
      examTypeId?: number;
    };
    
    if (!questions || questions.length === 0) {
      return NextResponse.json(
        { error: 'No questions provided' },
        { status: 400 }
      );
    }
    
    // Transform questions to match service format
    const transformedQuestions = questions.map(q => ({
      title: q.title,
      text: q.text,
      type: q.type as QuestionType,
      difficulty: q.difficulty,
      sectionId: q.sectionId || sectionId || 1,
      examTypeId: q.examTypeId || examTypeId || 1,
      options: q.options,
      isMockQuestion: true,
      metadata: {
        ...q.metadata,
        isContextual: q.type === 'contextual',
        addedAt: new Date().toISOString(),
      },
    }));
    
    // Add batch to database
    const results = await QuestionDistributionService.addQuestionBatch(transformedQuestions);
    
    return NextResponse.json({
      success: true,
      added: results.length,
      questionIds: results.map(r => r.problemid),
      distribution: {
        independent: questions.filter(q => q.type === 'independent').length,
        contextual: questions.filter(q => q.type === 'contextual').length,
        easy: questions.filter(q => q.difficulty <= 0).length,
        medium: questions.filter(q => q.difficulty >= 1 && q.difficulty <= 2).length,
        hard: questions.filter(q => q.difficulty >= 3).length,
      },
      addedAt: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('Error adding question batch:', error);
    return NextResponse.json(
      { error: 'Failed to add question batch' },
      { status: 500 }
    );
  }
}

// Example request body:
// {
//   "questions": [
//     {
//       "title": "What is 2 + 2?",
//       "text": "Calculate the sum",
//       "type": "independent",
//       "difficulty": 0,
//       "sectionId": 1,
//       "examTypeId": 1,
//       "options": [
//         { "text": "3", "isCorrect": false },
//         { "text": "4", "isCorrect": true },
//         { "text": "5", "isCorrect": false },
//         { "text": "6", "isCorrect": false }
//       ]
//     }
//   ],
//   "sectionId": 1,
//   "examTypeId": 1
// }
