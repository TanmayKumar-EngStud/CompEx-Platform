/**
 * Shuffle Algorithms Library
 * 
 * Advanced shuffling algorithms and utilities for question ordering.
 * Provides multiple shuffle strategies including performance-aware,
 * educational-focused, and weighted shuffling algorithms.
 */
// Force rebuild


export interface ShuffleOptions {
  /** Seed for reproducible shuffles (optional) */
  seed?: number;
  /** Preserve question groupings */
  preserveGroups?: boolean;
  /** Weight questions based on user performance */
  usePerformanceWeights?: boolean;
  /** Maximum number of consecutive questions from same category */
  maxConsecutiveCategory?: number;
  /** Ensure difficulty progression */
  maintainDifficultyProgression?: boolean;
}

export interface WeightedQuestion {
  id: string;
  weight: number;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  userAccuracy?: number;
  lastAttempted?: Date;
}

export interface ShuffleResult {
  shuffledIds: string[];
  algorithm: string;
  preservedOrder: boolean;
  seed?: number;
  metadata?: Record<string, any>;
}

/**
 * Standard Fisher-Yates shuffle algorithm
 * Provides uniform random distribution with O(n) time complexity
 */
export function fisherYatesShuffle<T>(array: T[], seed?: number): T[] {
  const shuffled = [...array];
  const random = seed ? createSeededRandom(seed) : Math.random;

  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  return shuffled;
}

/**
 * Performance-weighted shuffle algorithm
 * Shuffles questions with bias toward questions user struggles with
 */
export function performanceWeightedShuffle(
  questions: WeightedQuestion[],
  options: ShuffleOptions = {}
): ShuffleResult {
  if (!options.usePerformanceWeights) {
    return {
      shuffledIds: fisherYatesShuffle(questions.map(q => q.id), options.seed),
      algorithm: 'fisher-yates',
      preservedOrder: false,
      seed: options.seed
    };
  }

  // Create weighted pools based on user accuracy
  const strugglingQuestions = questions.filter(q => (q.userAccuracy || 1) < 0.6);
  const moderateQuestions = questions.filter(q => (q.userAccuracy || 1) >= 0.6 && (q.userAccuracy || 1) < 0.8);
  const strongQuestions = questions.filter(q => (q.userAccuracy || 1) >= 0.8);

  // Shuffle each pool separately
  const shuffledStruggling = fisherYatesShuffle(strugglingQuestions, options.seed);
  const shuffledModerate = fisherYatesShuffle(moderateQuestions, options.seed ? options.seed + 1 : undefined);
  const shuffledStrong = fisherYatesShuffle(strongQuestions, options.seed ? options.seed + 2 : undefined);

  // Interleave pools with bias toward struggling questions
  const result: WeightedQuestion[] = [];
  let strugglingIndex = 0;
  let moderateIndex = 0;
  let strongIndex = 0;

  // Distribution: 50% struggling, 30% moderate, 20% strong
  const pattern = [0, 0, 1, 0, 2, 0, 1, 0, 0, 1]; // 0=struggling, 1=moderate, 2=strong

  while (strugglingIndex < shuffledStruggling.length ||
    moderateIndex < shuffledModerate.length ||
    strongIndex < shuffledStrong.length) {

    const poolIndex = pattern[result.length % pattern.length];

    if (poolIndex === 0 && strugglingIndex < shuffledStruggling.length) {
      result.push(shuffledStruggling[strugglingIndex++]);
    } else if (poolIndex === 1 && moderateIndex < shuffledModerate.length) {
      result.push(shuffledModerate[moderateIndex++]);
    } else if (poolIndex === 2 && strongIndex < shuffledStrong.length) {
      result.push(shuffledStrong[strongIndex++]);
    } else {
      // Fall back to any available pool
      if (strugglingIndex < shuffledStruggling.length) {
        result.push(shuffledStruggling[strugglingIndex++]);
      } else if (moderateIndex < shuffledModerate.length) {
        result.push(shuffledModerate[moderateIndex++]);
      } else if (strongIndex < shuffledStrong.length) {
        result.push(shuffledStrong[strongIndex++]);
      }
    }
  }

  return {
    shuffledIds: result.map(q => q.id),
    algorithm: 'performance-weighted',
    preservedOrder: false,
    seed: options.seed,
    metadata: {
      strugglingCount: shuffledStruggling.length,
      moderateCount: shuffledModerate.length,
      strongCount: shuffledStrong.length
    }
  };
}

/**
 * Category-balanced shuffle algorithm
 * Ensures questions from different categories are well-distributed
 */
export function categoryBalancedShuffle(
  questions: WeightedQuestion[],
  options: ShuffleOptions = {}
): ShuffleResult {
  const maxConsecutive = options.maxConsecutiveCategory || 3;

  // Group questions by category
  const categoryGroups = new Map<string, WeightedQuestion[]>();
  for (const question of questions) {
    const category = question.category || 'uncategorized';
    if (!categoryGroups.has(category)) {
      categoryGroups.set(category, []);
    }
    categoryGroups.get(category)!.push(question);
  }

  // Shuffle each category group
  const shuffledGroups = new Map<string, WeightedQuestion[]>();
  let seedOffset = 0;
  for (const [category, group] of Array.from(categoryGroups.entries())) {
    const shuffled = fisherYatesShuffle(group, options.seed ? options.seed + seedOffset : undefined);
    shuffledGroups.set(category, shuffled);
    seedOffset++;
  }

  // Interleave categories to avoid consecutive questions from same category
  const result: WeightedQuestion[] = [];
  const categoryNames = Array.from(categoryGroups.keys());
  const categoryIndices = new Map<string, number>();
  categoryNames.forEach(cat => categoryIndices.set(cat, 0));

  let consecutiveCount = 0;
  let lastCategory = '';

  while (result.length < questions.length) {
    let selectedCategory = '';

    // Try to find a different category than the last one
    if (consecutiveCount < maxConsecutive) {
      // Can continue with same category
      const availableCategories = categoryNames.filter(cat => {
        const group = shuffledGroups.get(cat)!;
        const index = categoryIndices.get(cat)!;
        return index < group.length;
      });

      if (availableCategories.length > 0) {
        // Prefer different category if possible
        const differentCategories = availableCategories.filter(cat => cat !== lastCategory);
        selectedCategory = differentCategories.length > 0
          ? differentCategories[0]
          : availableCategories[0];
      }
    } else {
      // Must switch category
      const availableCategories = categoryNames.filter(cat => {
        const group = shuffledGroups.get(cat)!;
        const index = categoryIndices.get(cat)!;
        return index < group.length && cat !== lastCategory;
      });

      if (availableCategories.length > 0) {
        selectedCategory = availableCategories[0];
      } else {
        // No choice but to continue with same category
        const anyAvailable = categoryNames.find(cat => {
          const group = shuffledGroups.get(cat)!;
          const index = categoryIndices.get(cat)!;
          return index < group.length;
        });
        selectedCategory = anyAvailable || '';
      }
    }

    if (selectedCategory) {
      const group = shuffledGroups.get(selectedCategory)!;
      const index = categoryIndices.get(selectedCategory)!;
      const question = group[index];

      result.push(question);
      categoryIndices.set(selectedCategory, index + 1);

      if (selectedCategory === lastCategory) {
        consecutiveCount++;
      } else {
        consecutiveCount = 1;
        lastCategory = selectedCategory;
      }
    } else {
      break; // No more questions available
    }
  }

  return {
    shuffledIds: result.map(q => q.id),
    algorithm: 'category-balanced',
    preservedOrder: false,
    seed: options.seed,
    metadata: {
      categories: categoryNames,
      maxConsecutive,
      categoryDistribution: Object.fromEntries(
        categoryNames.map(cat => [cat, categoryGroups.get(cat)!.length])
      )
    }
  };
}

/**
 * Difficulty-progressive shuffle algorithm
 * Ensures a gradual increase in difficulty throughout the question set
 */
export function difficultyProgressiveShuffle(
  questions: WeightedQuestion[],
  options: ShuffleOptions = {}
): ShuffleResult {
  if (!options.maintainDifficultyProgression) {
    return {
      shuffledIds: fisherYatesShuffle(questions.map(q => q.id), options.seed),
      algorithm: 'fisher-yates',
      preservedOrder: false,
      seed: options.seed
    };
  }

  // Group by difficulty
  const easyQuestions = questions.filter(q => q.difficulty === 'easy');
  const mediumQuestions = questions.filter(q => q.difficulty === 'medium');
  const hardQuestions = questions.filter(q => q.difficulty === 'hard');
  const unspecifiedQuestions = questions.filter(q => !q.difficulty);

  // Shuffle within each difficulty level
  const shuffledEasy = fisherYatesShuffle(easyQuestions, options.seed);
  const shuffledMedium = fisherYatesShuffle(mediumQuestions, options.seed ? options.seed + 1 : undefined);
  const shuffledHard = fisherYatesShuffle(hardQuestions, options.seed ? options.seed + 2 : undefined);
  const shuffledUnspecified = fisherYatesShuffle(unspecifiedQuestions, options.seed ? options.seed + 3 : undefined);

  // Create progressive distribution
  const result: WeightedQuestion[] = [];
  const totalQuestions = questions.length;

  // Distribution pattern: 60% easy in first third, 70% medium in middle third, 60% hard in last third
  const easyTargetInFirstThird = Math.floor(totalQuestions / 3 * 0.6);
  const mediumTargetInMiddleThird = Math.floor(totalQuestions / 3 * 0.7);
  const hardTargetInLastThird = Math.floor(totalQuestions / 3 * 0.6);

  let easyIndex = 0, mediumIndex = 0, hardIndex = 0, unspecifiedIndex = 0;

  // First third: mostly easy
  const firstThirdEnd = Math.floor(totalQuestions / 3);
  for (let i = 0; i < firstThirdEnd; i++) {
    if (easyIndex < shuffledEasy.length && result.filter(q => q.difficulty === 'easy').length < easyTargetInFirstThird) {
      result.push(shuffledEasy[easyIndex++]);
    } else if (mediumIndex < shuffledMedium.length) {
      result.push(shuffledMedium[mediumIndex++]);
    } else if (unspecifiedIndex < shuffledUnspecified.length) {
      result.push(shuffledUnspecified[unspecifiedIndex++]);
    } else if (easyIndex < shuffledEasy.length) {
      result.push(shuffledEasy[easyIndex++]);
    } else if (hardIndex < shuffledHard.length) {
      result.push(shuffledHard[hardIndex++]);
    }
  }

  // Second third: mostly medium
  const secondThirdEnd = Math.floor(totalQuestions * 2 / 3);
  for (let i = firstThirdEnd; i < secondThirdEnd; i++) {
    if (mediumIndex < shuffledMedium.length && result.filter(q => q.difficulty === 'medium').length < mediumTargetInMiddleThird + result.filter(q => q.difficulty === 'medium').length) {
      result.push(shuffledMedium[mediumIndex++]);
    } else if (easyIndex < shuffledEasy.length) {
      result.push(shuffledEasy[easyIndex++]);
    } else if (hardIndex < shuffledHard.length) {
      result.push(shuffledHard[hardIndex++]);
    } else if (unspecifiedIndex < shuffledUnspecified.length) {
      result.push(shuffledUnspecified[unspecifiedIndex++]);
    }
  }

  // Last third: mostly hard
  for (let i = secondThirdEnd; i < totalQuestions; i++) {
    if (hardIndex < shuffledHard.length) {
      result.push(shuffledHard[hardIndex++]);
    } else if (mediumIndex < shuffledMedium.length) {
      result.push(shuffledMedium[mediumIndex++]);
    } else if (easyIndex < shuffledEasy.length) {
      result.push(shuffledEasy[easyIndex++]);
    } else if (unspecifiedIndex < shuffledUnspecified.length) {
      result.push(shuffledUnspecified[unspecifiedIndex++]);
    }
  }

  return {
    shuffledIds: result.map(q => q.id),
    algorithm: 'difficulty-progressive',
    preservedOrder: false,
    seed: options.seed,
    metadata: {
      easyCount: shuffledEasy.length,
      mediumCount: shuffledMedium.length,
      hardCount: shuffledHard.length,
      unspecifiedCount: shuffledUnspecified.length,
      progressiveDistribution: true
    }
  };
}

/**
 * Spaced repetition shuffle algorithm
 * Prioritizes questions that need review based on spaced repetition intervals
 */
export function spacedRepetitionShuffle(
  questions: WeightedQuestion[],
  options: ShuffleOptions = {}
): ShuffleResult {
  const now = new Date();

  // Calculate review priorities based on last attempted date and accuracy
  const questionsWithPriority = questions.map(q => {
    const daysSinceLastAttempt = q.lastAttempted
      ? (now.getTime() - q.lastAttempted.getTime()) / (1000 * 60 * 60 * 24)
      : 30; // Default to 30 days if never attempted

    const accuracy = q.userAccuracy || 0.5;

    // Higher priority for: low accuracy, long time since last attempt
    const priority = (1 - accuracy) * 10 + Math.min(daysSinceLastAttempt / 7, 5);

    return { ...q, priority };
  });

  // Sort by priority (highest first) then shuffle within priority groups
  questionsWithPriority.sort((a, b) => b.priority - a.priority);

  // Group into priority tiers
  const highPriority = questionsWithPriority.slice(0, Math.floor(questions.length * 0.4));
  const mediumPriority = questionsWithPriority.slice(Math.floor(questions.length * 0.4), Math.floor(questions.length * 0.7));
  const lowPriority = questionsWithPriority.slice(Math.floor(questions.length * 0.7));

  // Shuffle within each tier
  const shuffledHigh = fisherYatesShuffle(highPriority, options.seed);
  const shuffledMedium = fisherYatesShuffle(mediumPriority, options.seed ? options.seed + 1 : undefined);
  const shuffledLow = fisherYatesShuffle(lowPriority, options.seed ? options.seed + 2 : undefined);

  // Interleave with bias toward high priority
  const result: WeightedQuestion[] = [];
  let highIndex = 0, mediumIndex = 0, lowIndex = 0;

  // Pattern: 60% high, 25% medium, 15% low priority
  const pattern = [0, 0, 0, 1, 0, 2, 0, 1, 0, 0]; // 0=high, 1=medium, 2=low

  while (highIndex < shuffledHigh.length ||
    mediumIndex < shuffledMedium.length ||
    lowIndex < shuffledLow.length) {

    const tierIndex = pattern[result.length % pattern.length];

    if (tierIndex === 0 && highIndex < shuffledHigh.length) {
      result.push(shuffledHigh[highIndex++]);
    } else if (tierIndex === 1 && mediumIndex < shuffledMedium.length) {
      result.push(shuffledMedium[mediumIndex++]);
    } else if (tierIndex === 2 && lowIndex < shuffledLow.length) {
      result.push(shuffledLow[lowIndex++]);
    } else {
      // Fall back to any available tier
      if (highIndex < shuffledHigh.length) {
        result.push(shuffledHigh[highIndex++]);
      } else if (mediumIndex < shuffledMedium.length) {
        result.push(shuffledMedium[mediumIndex++]);
      } else if (lowIndex < shuffledLow.length) {
        result.push(shuffledLow[lowIndex++]);
      }
    }
  }

  return {
    shuffledIds: result.map(q => q.id),
    algorithm: 'spaced-repetition',
    preservedOrder: false,
    seed: options.seed,
    metadata: {
      highPriorityCount: shuffledHigh.length,
      mediumPriorityCount: shuffledMedium.length,
      lowPriorityCount: shuffledLow.length,
      avgHighPriority: shuffledHigh.reduce((sum, q) => sum + q.priority, 0) / shuffledHigh.length,
      avgMediumPriority: shuffledMedium.reduce((sum, q) => sum + q.priority, 0) / shuffledMedium.length,
      avgLowPriority: shuffledLow.reduce((sum, q) => sum + q.priority, 0) / shuffledLow.length
    }
  };
}

/**
 * Create a seeded random number generator
 * Uses a simple Linear Congruential Generator for reproducible randomness
 */
function createSeededRandom(seed: number): () => number {
  let currentSeed = seed;
  return function () {
    currentSeed = (currentSeed * 1664525 + 1013904223) % 4294967296;
    return currentSeed / 4294967296;
  };
}

/**
 * Advanced shuffle function that chooses the best algorithm based on context
 */
export function smartShuffle(
  questions: WeightedQuestion[],
  options: ShuffleOptions = {}
): ShuffleResult {
  // Determine the best shuffle algorithm based on available data and options

  if (options.usePerformanceWeights && questions.some(q => q.userAccuracy !== undefined)) {
    return performanceWeightedShuffle(questions, options);
  }

  if (options.maintainDifficultyProgression && questions.some(q => q.difficulty !== undefined)) {
    return difficultyProgressiveShuffle(questions, options);
  }

  if (options.maxConsecutiveCategory && questions.some(q => q.category !== undefined)) {
    return categoryBalancedShuffle(questions, options);
  }

  if (questions.some(q => q.lastAttempted !== undefined || q.userAccuracy !== undefined)) {
    return spacedRepetitionShuffle(questions, options);
  }

  // Fall back to basic Fisher-Yates shuffle
  return {
    shuffledIds: fisherYatesShuffle(questions.map(q => q.id), options.seed),
    algorithm: 'fisher-yates',
    preservedOrder: false,
    seed: options.seed
  };
}

/**
 * Utility to convert simple ID array to WeightedQuestion array
 */
export function createWeightedQuestions(
  questionIds: string[],
  weights?: Record<string, Partial<WeightedQuestion>>
): WeightedQuestion[] {
  return questionIds.map(id => ({
    id,
    weight: 1,
    ...weights?.[id]
  }));
}

/**
 * Validate shuffle result integrity
 */
export function validateShuffleResult(
  originalIds: string[],
  shuffleResult: ShuffleResult
): boolean {
  const { shuffledIds } = shuffleResult;

  // Check same length
  if (originalIds.length !== shuffledIds.length) {
    console.warn('Shuffle validation failed: length mismatch');
    return false;
  }

  // Check all original IDs are present
  const originalSet = new Set(originalIds);
  const shuffledSet = new Set(shuffledIds);

  if (originalSet.size !== shuffledSet.size) {
    console.warn('Shuffle validation failed: duplicate IDs in result');
    return false;
  }

  for (const id of originalIds) {
    if (!shuffledSet.has(id)) {
      console.warn(`Shuffle validation failed: missing ID ${id}`);
      return false;
    }
  }

  return true;
}