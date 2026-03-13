# 📊 Compex Question Distribution System

Smart question distribution for balanced mock papers.

## Overview

This system ensures mock papers have:
- **Balanced question types** (independent vs contextual)
- **Proper difficulty spread** (easy, medium, hard)
- **Topic coverage** (all topics represented)
- **Quality thresholds** (only good questions used)

## Problem Solved

```
Before: Random question selection → Unbalanced mock papers
After:  Smart distribution → Balanced, fair mock papers
```

## Usage

### Generate Balanced Mock Paper

```typescript
import { QuestionDistributionService } from '@/features/question-distribution';

const result = await QuestionDistributionService.generateMockPaper({
  independentRatio: 0.6,  // 60% independent
  contextualRatio: 0.4,   // 40% contextual
  easyRatio: 0.2,         // 20% easy
  mediumRatio: 0.5,       // 50% medium
  hardRatio: 0.3,         // 30% hard
  batchSize: 10,          // 10 questions per paper
  minQualityScore: 0.3,   // Only good questions
});

console.log(result.distribution);
// Output: { independent: 6, contextual: 4, easy: 2, medium: 5, hard: 3, topics: [...] }
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mock-papers/generate` | GET | Generate balanced mock paper |
| `/api/questions/distribution/stats` | GET | Get distribution analytics |
| `/api/questions/batch/add` | POST | Add question batch |

### Example: Generate Mock Paper

```bash
GET /api/mock-papers/generate?batchSize=20&independentRatio=0.7
```

Response:
```json
{
  "success": true,
  "mockPaper": {
    "questions": [
      { "id": 1, "title": "...", "type": "independent", "difficulty": 1, "topic": "Algebra" },
      { "id": 2, "title": "...", "type": "contextual", "difficulty": 2, "topic": "Geometry" }
    ],
    "distribution": {
      "independent": 14,
      "contextual": 6,
      "easy": 4,
      "medium": 10,
      "hard": 6,
      "topics": ["Algebra", "Geometry", "Statistics"]
    },
    "source": "batch",
    "remainingInBatch": 45
  }
}
```

### Example: Add Question Batch

```bash
POST /api/questions/batch/add
Content-Type: application/json

{
  "questions": [
    {
      "title": "Solve for x",
      "text": "2x + 5 = 15",
      "type": "independent",
      "difficulty": 1,
      "sectionId": 1,
      "examTypeId": 1,
      "options": [
        { "text": "5", "isCorrect": true },
        { "text": "10", "isCorrect": false }
      ]
    }
  ]
}
```

## Question Types

| Type | Description | Example |
|------|-------------|---------|
| `independent` | Standalone questions | "What is 2+2?" |
| `contextual` | Questions with context | "In the previous passage..." |

## Difficulty Levels

| Level | Numeric | Percentage |
|-------|---------|------------|
| Easy | 0 | 20% |
| Medium | 1-2 | 50% |
| Hard | 3+ | 30% |

## Configuration Options

```typescript
interface DistributionConfig {
  // Question type balance (must sum to 1.0)
  independentRatio: number;   // e.g., 0.6
  contextualRatio: number;    // e.g., 0.4
  
  // Difficulty spread (must sum to 1.0)
  easyRatio: number;          // e.g., 0.2
  mediumRatio: number;        // e.g., 0.5
  hardRatio: number;          // e.g., 0.3
  
  // Coverage settings
  requireTopicCoverage: boolean;  // Ensure all topics
  minTopicsRequired: number;      // Minimum topics
  
  // Quality settings
  batchSize: number;          // Questions per batch
  minQualityScore: number;    // Quality threshold (0-1)
}
```

## Analytics

Get distribution insights:

```bash
GET /api/questions/distribution/stats
```

Response includes:
- Total questions by type
- Difficulty breakdown
- Section coverage
- Quality metrics
- Recommendations

## Files

```
features/question-distribution/
├── question-distribution.ts    # Main service
├── index.ts                    # Exports
└── README.md                   # This file

app/api/
├── mock-papers/generate/route.ts        # Generate mock papers
├── questions/distribution/stats/route.ts # Analytics
└── questions/batch/add/route.ts          # Add questions
```

## Adding New Questions

### From External Source (CSV, API, etc.)

```typescript
const newQuestions = [
  {
    title: "Question 1",
    text: "...",
    type: "independent" as const,
    difficulty: 1,
    sectionId: 1,
    examTypeId: 1,
    options: [...]
  }
];

await QuestionDistributionService.addQuestionBatch(newQuestions);
```

### With Antigravity AI

After AI generates questions:
1. Parse AI output
2. Transform to QuestionBatchItem format
3. POST to `/api/questions/batch/add`

## Quality Scores

Questions are scored based on:
- `popularityIndex` - User engagement
- `totalAttempts` - How many times attempted
- `correctAttemptRate` - Accuracy rate

Higher quality = more likely to be selected.

## Recommendations

The system generates recommendations:

| Status | Message |
|--------|---------|
| ✅ | Good balance detected |
| 🟡 | Adjust distribution |
| 🔴 | Critical issue (too few questions) |

## Future Improvements

- [ ] ML-based difficulty estimation
- [ ] Adaptive difficulty based on user
- [ ] Time-based distribution (newer questions weighted)
- [ ] Performance correlation analysis
- [ ] Cross-topic question linking

## Integration with Antigravity AI

When AI generates questions:
1. AI outputs JSON with question metadata
2. System validates format
3. Distributes across types/difficulties
4. Adds to rotation pool
5. Marks for quality review after use
