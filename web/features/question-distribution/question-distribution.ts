// Question Distribution Service for Mock Papers
// Balances independent vs contextual questions from pre-generated batches

import { prisma } from '@/lib/prisma';

export type QuestionType = 'independent' | 'contextual';
export type DifficultyLevel = 'easy' | 'medium' | 'hard';

export interface DistributionConfig {
  // Target distribution percentages
  independentRatio: number;      // e.g., 0.6 = 60% independent
  contextualRatio: number;       // e.g., 0.4 = 40% contextual
  
  // Difficulty spread
  easyRatio: number;             // e.g., 0.2 = 20% easy
  mediumRatio: number;           // e.g., 0.5 = 50% medium
  hardRatio: number;             // e.g., 0.3 = 30% hard
  
  // Topic coverage
  requireTopicCoverage: boolean; // Ensure all topics represented
  minTopicsRequired: number;     // Minimum different topics
  
  // Batch settings
  batchSize: number;             // Questions per batch
  isMockQuestion: boolean;       // Only use mock questions
  
  // Quality settings
  minQualityScore: number;       // Minimum quality threshold (0-1)
  allowRegenerating: boolean;    // Include questions marked for regeneration
}

export interface QuestionCandidate {
  problemid: number;
  title: string;
  type: QuestionType;
  difficulty: number;            // 0-3 scale
  topicId?: number;
  topicName?: string;
  qualityScore: number;
  popularityIndex: number;
  totalAttempts: number;
  correctAttemptRate: number;
}

export interface DistributionResult {
  questions: QuestionCandidate[];
  distribution: {
    independent: number;
    contextual: number;
    easy: number;
    medium: number;
    hard: number;
    topics: string[];
  };
  source: 'batch' | 'database' | 'mixed';
  remainingInBatch: number;
}

export const DEFAULT_CONFIG: DistributionConfig = {
  independentRatio: 0.6,         // 60% independent
  contextualRatio: 0.4,          // 40% contextual
  easyRatio: 0.2,                // 20% easy
  mediumRatio: 0.5,              // 50% medium
  hardRatio: 0.3,                // 30% hard
  requireTopicCoverage: true,
  minTopicsRequired: 3,
  batchSize: 10,
  isMockQuestion: true,
  minQualityScore: 0.3,
  allowRegenerating: false,
};

// Distribution cache for current batch
let questionBatchCache: QuestionCandidate[] = [];
let currentBatchId: string | null = null;

export class QuestionDistributionService {
  
  /**
   * Generate a balanced set of questions for a mock paper
   */
  static async generateMockPaper(config: Partial<DistributionConfig> = {}): Promise<DistributionResult> {
    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    
    // Check if we have a valid cached batch
    if (!this.isValidBatch(currentBatchId)) {
      await this.loadNewBatch(finalConfig);
    }
    
    // Select questions from batch
    const selected = this.selectFromBatch(finalConfig);
    
    return {
      questions: selected,
      distribution: this.analyzeDistribution(selected),
      source: this.getSource(),
      remainingInBatch: questionBatchCache.length,
    };
  }
  
  /**
   * Load a new batch of questions from database
   */
  private static async loadNewBatch(config: DistributionConfig): Promise<void> {
    // Get available questions from database
    const questions = await prisma.problems.findMany({
      where: {
        isMockQuestion: true,
        popularityIndex: { gte: config.minQualityScore },
        ...(config.allowRegenerating ? {} : {
          // Exclude questions marked for regeneration
          NOT: {
            metadata: { path: ['needsRegeneration'], equals: true }
          }
        }),
      },
      include: {
        sections: {
          select: { sectionid: true, name: true }
        },
        problemtags: {
          include: {
            tag_scopes: {
              include: {
                tags: { select: { name: true } }
              }
            }
          }
        }
      },
      orderBy: { popularityIndex: 'desc' },
      take: config.batchSize * 3, // Get extra to allow selection
    });
    
    // Transform to candidates
    questionBatchCache = questions.map(q => this.toCandidate(q));
    currentBatchId = this.generateBatchId();
    
    console.log(`📦 Loaded batch of ${questionBatchCache.length} questions`);
  }
  
  /**
   * Select questions ensuring balanced distribution
   */
  private static selectFromBatch(config: DistributionConfig): QuestionCandidate[] {
    const selected: QuestionCandidate[] = [];
    const targetCount = config.batchSize;
    
    // Calculate target counts
    const targetIndependent = Math.floor(targetCount * config.independentRatio);
    const targetContextual = targetCount - targetIndependent;
    
    const targetEasy = Math.floor(targetCount * config.easyRatio);
    const targetMedium = Math.floor(targetCount * config.mediumRatio);
    const targetHard = targetCount - targetEasy - targetMedium;
    
    // Group questions by type and difficulty
    const independent = questionBatchCache.filter(q => q.type === 'independent');
    const contextual = questionBatchCache.filter(q => q.type === 'contextual');
    
    // Select by type (alternating for balance)
    const typeSelection = this.balanceSelection(
      independent,
      contextual,
      targetIndependent,
      targetContextual
    );
    
    // Within each type, select by difficulty
    for (const q of typeSelection) {
      if (selected.length >= targetCount) break;
      
      const difficultyGroup = this.getDifficultyGroup(q.difficulty);
      const currentInGroup = selected.filter(s => this.getDifficultyGroup(s.difficulty) === difficultyGroup).length;
      const targetInGroup = this.getTargetForGroup(difficultyGroup, config);
      
      if (currentInGroup < targetInGroup) {
        selected.push(q);
      } else if (selected.length < targetCount * 0.8) {
        // Allow some flexibility - add if we're under 80% of target
        selected.push(q);
      }
    }
    
    // If we don't have enough, fill with remaining
    const remaining = questionBatchCache.filter(q => !selected.includes(q));
    while (selected.length < targetCount && remaining.length > 0) {
      selected.push(remaining.shift()!);
    }
    
    return selected;
  }
  
  /**
   * Balance selection between two groups
   */
  private static balanceSelection(
    groupA: QuestionCandidate[],
    groupB: QuestionCandidate[],
    targetA: number,
    targetB: number
  ): QuestionCandidate[] {
    const result: QuestionCandidate[] = [];
    let indexA = 0;
    let indexB = 0;
    
    while (result.length < targetA + targetB) {
      // Alternate between groups
      if (indexA < groupA.length && (result.length % 2 === 0 || indexB >= groupB.length)) {
        result.push(groupA[indexA++]);
      } else if (indexB < groupB.length) {
        result.push(groupB[indexB++]);
      } else if (indexA < groupA.length) {
        result.push(groupA[indexA++]);
      } else {
        break;
      }
    }
    
    return result;
  }
  
  /**
   * Get difficulty group from difficulty level
   */
  private static getDifficultyGroup(difficulty: number): DifficultyLevel {
    if (difficulty <= 0) return 'easy';
    if (difficulty <= 2) return 'medium';
    return 'hard';
  }
  
  /**
   * Get target count for difficulty group
   */
  private static getTargetForGroup(group: DifficultyLevel, config: DistributionConfig): number {
    switch (group) {
      case 'easy': return Math.floor(config.batchSize * config.easyRatio);
      case 'medium': return Math.floor(config.batchSize * config.mediumRatio);
      case 'hard': return config.batchSize - Math.floor(config.batchSize * config.easyRatio) - Math.floor(config.batchSize * config.mediumRatio);
      default: return 0;
    }
  }
  
  /**
   * Analyze the distribution of selected questions
   */
  private static analyzeDistribution(questions: QuestionCandidate[]) {
    return {
      independent: questions.filter(q => q.type === 'independent').length,
      contextual: questions.filter(q => q.type === 'contextual').length,
      easy: questions.filter(q => this.getDifficultyGroup(q.difficulty) === 'easy').length,
      medium: questions.filter(q => this.getDifficultyGroup(q.difficulty) === 'medium').length,
      hard: questions.filter(q => this.getDifficultyGroup(q.difficulty) === 'hard').length,
      topics: [...new Set(questions.map(q => q.topicName).filter(Boolean))] as string[],
    };
  }
  
  /**
   * Get source of questions
   */
  private static getSource(): 'batch' | 'database' | 'mixed' {
    if (questionBatchCache.length > DEFAULT_CONFIG.batchSize) return 'batch';
    return 'database';
  }
  
  /**
   * Check if batch is valid
   */
  private static isValidBatch(batchId: string | null): boolean {
    if (!batchId) return false;
    return true; // Could add time-based expiration
  }
  
  /**
   * Generate unique batch ID
   */
  private static generateBatchId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Transform Prisma model to candidate
   */
  private static toCandidate(problem: any): QuestionCandidate {
    // Determine if question is contextual or independent
    const type = problem.metadata?.isContextual ? 'contextual' : 'independent';
    
    // Calculate difficulty based on user performance
    const difficulty = problem.difficulty || 1;
    
    // Get topic
    const topic = problem.problemtags?.[0]?.tag_scopes?.tags?.name || 'General';
    
    return {
      problemid: problem.problemid,
      title: problem.title,
      type,
      difficulty,
      topicId: problem.sectionid,
      topicName: topic,
      qualityScore: problem.popularityIndex,
      popularityIndex: problem.popularityIndex,
      totalAttempts: problem.totalattemptscount || 0,
      correctAttemptRate: problem.totalattemptscount > 0
        ? (problem.correctattemptscount / problem.totalattemptscount)
        : 0.5,
    };
  }
  
  /**
   * Get current batch statistics
   */
  static async getBatchStats() {
    if (questionBatchCache.length === 0) {
      await this.loadNewBatch(DEFAULT_CONFIG);
    }
    
    const distribution = this.analyzeDistribution(questionBatchCache);
    
    return {
      totalQuestions: questionBatchCache.length,
      distribution,
      avgQuality: questionBatchCache.reduce((sum, q) => sum + q.qualityScore, 0) / questionBatchCache.length,
      avgDifficulty: questionBatchCache.reduce((sum, q) => sum + q.difficulty, 0) / questionBatchCache.length,
    };
  }
  
  /**
   * Add new question batch to database
   */
  static async addQuestionBatch(questions: {
    title: string;
    text: string;
    type: QuestionType;
    difficulty: number;
    sectionId: number;
    examTypeId: number;
    options: { text: string; isCorrect: boolean }[];
    isMockQuestion?: boolean;
    metadata?: Record<string, any>;
  }[]) {
    const results = [];
    
    for (const q of questions) {
      const problem = await prisma.problems.create({
        data: {
          title: q.title,
          text: q.text,
          difficulty: q.difficulty,
          sectionid: q.sectionId,
          examtypeid: q.examTypeId,
          isMockQuestion: q.isMockQuestion ?? true,
          metadata: q.metadata || {},
          problemoptions: {
            create: q.options.map((opt, idx) => ({
              optiontext: opt.text,
              iscorrect: opt.isCorrect,
              group: String.fromCharCode(65 + idx),
            })),
          },
        },
      });
      results.push(problem);
    }
    
    // Invalidate cache so new questions are included
    currentBatchId = null;
    
    return results;
  }
  
  /**
   * Get distribution analytics
   */
  static async getDistributionAnalytics() {
    const total = await prisma.problems.count({
      where: { isMockQuestion: true },
    });
    
    const byType = await prisma.problems.groupBy({
      by: ['isChildren'],
      where: { isMockQuestion: true },
      _count: true,
    });
    
    const byDifficulty = await prisma.problems.groupBy({
      by: ['difficulty'],
      where: { isMockQuestion: true },
      _count: true,
    });
    
    return {
      total,
      byType: {
        independent: byType.find(g => g.isChildren === false)?._count || 0,
        contextual: byType.find(g => g.isChildren === true)?._count || 0,
      },
      byDifficulty: byDifficulty.map(d => ({
        level: d.difficulty,
        count: d._count,
      })),
    };
  }
}
