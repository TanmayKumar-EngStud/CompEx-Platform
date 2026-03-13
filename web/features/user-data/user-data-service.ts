// User Data Export/Import Service
// Users own their data - transparent, portable, secure

import { prisma } from '@/lib/prisma';
import { encrypt, decrypt } from '@/utils/crypto';

// Data types that users can export
export interface UserDataPackage {
  version: string;
  exportedAt: string;
  user: {
    userid: number;
    username: string;
    email: string;
    registrationdate: string;
  };
  progress: {
    totalQuestions: number;
    totalCorrect: number;
    overallAccuracy: number;
    topics: TopicProgress[];
    difficultyBreakdown: DifficultyBreakdown;
    streakData: StreakData | null;
  };
  analytics: {
    weeklyActivity: WeeklyActivity[];
    strongTopics: string[];
    weakTopics: string[];
    averageTimePerQuestion: number;
    improvementTrend: string;
  };
  preferences: {
    theme: string;
    notifications: boolean;
    dailyGoal: number;
    difficultyPreference: string;
  };
  achievements: {
    badges: Badge[];
    milestones: Milestone[];
    collectibles: Collectible[];
  };
}

export interface TopicProgress {
  topicName: string;
  questionsAttempted: number;
  correct: number;
  accuracy: number;
  averageTime: number;
  lastAttempted: string;
}

export interface DifficultyBreakdown {
  easy: { attempted: number; correct: number; accuracy: number };
  medium: { attempted: number; correct: number; accuracy: number };
  hard: { attempted: number; correct: number; accuracy: number };
}

export interface StreakData {
  currentStreak: number;
  longestStreak: number;
  lastActiveDate: string;
  totalActiveDays: number;
}

export interface WeeklyActivity {
  date: string;
  questionsAnswered: number;
  timeSpent: number;
}

export interface Badge {
  id: string;
  name: string;
  earnedAt: string;
  description: string;
}

export interface Milestone {
  id: string;
  name: string;
  achievedAt: string;
  progress: number;
}

export interface Collectible {
  id: number;
  type: string;
  name: string;
  earnedAt: string;
  icon: string;
}

class UserDataService {
  /**
   * Export all user data - User owns this data
   */
  static async exportUserData(userId: number): Promise<UserDataPackage> {
    // Fetch all user data
    const user = await prisma.users.findUnique({
      where: { userid: userId },
      select: {
        userid: true,
        username: true,
        email: true,
        registrationdate: true,
      },
    });

    // Fetch progress data
    const attempts = await prisma.userattempts.findMany({
      where: { userid: userId },
      include: {
        problems: {
          select: {
            sectionid: true,
            difficulty: true,
          },
        },
      },
      orderBy: { attemptdate: 'desc' },
    });

    const totalQuestions = attempts.length;
    const totalCorrect = attempts.filter((a) => a.iscorrect).length;
    const overallAccuracy = totalQuestions > 0 ? (totalCorrect / totalQuestions) * 100 : 0;

    // Calculate topic progress
    const topicMap = new Map<string, TopicProgress>();
    const difficultyBreakdown: DifficultyBreakdown = {
      easy: { attempted: 0, correct: 0, accuracy: 0 },
      medium: { attempted: 0, correct: 0, accuracy: 0 },
      hard: { attempted: 0, correct: 0, accuracy: 0 },
    };

    attempts.forEach((attempt) => {
      const sectionId = attempt.problems?.sectionid || 0;
      const difficulty = attempt.problems?.difficulty || 1;

      // Track by difficulty
      if (difficulty <= 0) {
        difficultyBreakdown.easy.attempted++;
        if (attempt.iscorrect) difficultyBreakdown.easy.correct++;
      } else if (difficulty <= 2) {
        difficultyBreakdown.medium.attempted++;
        if (attempt.iscorrect) difficultyBreakdown.medium.correct++;
      } else {
        difficultyBreakdown.hard.attempted++;
        if (attempt.iscorrect) difficultyBreakdown.hard.correct++;
      }

      // Track by section
      const key = `section-${sectionId}`;
      if (!topicMap.has(key)) {
        topicMap.set(key, {
          topicName: `Section ${sectionId}`,
          questionsAttempted: 0,
          correct: 0,
          accuracy: 0,
          averageTime: 0,
          lastAttempted: attempt.attemptdate?.toISOString() || '',
        });
      }
      const topic = topicMap.get(key)!;
      topic.questionsAttempted++;
      if (attempt.iscorrect) topic.correct++;
      topic.lastAttempted = attempt.attemptdate?.toISOString() || '';
    });

    // Calculate accuracies
    topicMap.forEach((topic) => {
      topic.accuracy = topic.questionsAttempted > 0 
        ? (topic.correct / topic.questionsAttempted) * 100 
        : 0;
    });

    const topics = Array.from(topicMap.values());

    // Fetch streak data
    const streak = await prisma.userstreaks.findFirst({
      where: { userid: userId },
    });

    const streakData: StreakData | null = streak ? {
      currentStreak: streak.currentstreak || 0,
      longestStreak: streak.higheststreak || 0,
      lastActiveDate: streak.lasttestdate?.toISOString() || '',
      totalActiveDays: streak.currentstreak || 0,
    } : null;

    // Calculate weekly activity
    const weeklyActivity: WeeklyActivity[] = [];
    const now = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const dayAttempts = attempts.filter((a) => {
        const attemptDate = a.attemptdate?.toISOString().split('T')[0];
        return attemptDate === dateStr;
      });

      weeklyActivity.push({
        date: dateStr,
        questionsAnswered: dayAttempts.length,
        timeSpent: dayAttempts.reduce((acc, a) => {
          const timeStr = a.timetaken?.toString() || '0';
          const seconds = parseInt(timeStr.replace(/\D/g, '') || '0', 10);
          return acc + seconds;
        }, 0),
      });
    }

    // Fetch preferences
    const settings = await prisma.users.findUnique({
      where: { userid: userId },
      select: { userid: true },
    });

    // Fetch achievements
    const userCollectibles = await prisma.userCollectible.findMany({
      where: { userId },
      orderBy: { earnedAt: 'desc' },
    });

    const collectibles: Collectible[] = userCollectibles.map((c) => ({
      id: c.id,
      type: c.collectibleType,
      name: c.collectibleName,
      earnedAt: c.earnedAt.toISOString(),
      icon: c.collectibleIcon || '',
    }));

    // Build the package
    const dataPackage: UserDataPackage = {
      version: '1.0.0',
      exportedAt: new Date().toISOString(),
      user: {
        userid: user?.userid || 0,
        username: user?.username || '',
        email: user?.email || '',
        registrationdate: user?.registrationdate?.toISOString() || '',
      },
      progress: {
        totalQuestions,
        totalCorrect,
        overallAccuracy,
        topics,
        difficultyBreakdown,
        streakData,
      },
      analytics: {
        weeklyActivity,
        strongTopics: topics.filter((t) => t.accuracy > 70).map((t) => t.topicName),
        weakTopics: topics.filter((t) => t.accuracy < 50).map((t) => t.topicName),
        averageTimePerQuestion: totalQuestions > 0
          ? attempts.reduce((acc, a) => {
              const timeStr = a.timetaken?.toString() || '0';
              const seconds = parseInt(timeStr.replace(/\D/g, '') || '0', 10);
              return acc + seconds;
            }, 0) / totalQuestions
          : 0,
        improvementTrend: overallAccuracy > 60 ? 'improving' : 'needsPractice',
      },
      preferences: {
        theme: 'system',
        notifications: true,
        dailyGoal: 10,
        difficultyPreference: 'balanced',
      },
      achievements: {
        badges: [],
        milestones: [],
        collectibles,
      },
    };

    return dataPackage;
  }

  /**
   * Import user data - Restore progress from backup
   */
  static async importUserData(
    userId: number,
    dataPackage: UserDataPackage
  ): Promise<{ success: boolean; message: string; restoredItems: number }> {
    let restoredItems = 0;

    try {
      // Validate package version
      if (dataPackage.version !== '1.0.0') {
        return {
          success: false,
          message: 'Incompatible data version. Please export fresh data.',
          restoredItems: 0,
        };
      }

      // Restore preferences (simple ones)
      // Note: We don't overwrite user account info
      // Only restore learning progress, not credentials

      // Restore achievements/collectibles
      if (dataPackage.achievements.collectibles.length > 0) {
        for (const collectible of dataPackage.achievements.collectibles) {
          await prisma.userCollectible.upsert({
            where: {
              id: collectible.id,
            },
            create: {
              id: collectible.id,
              userId,
              collectibleType: collectible.type,
              collectibleName: collectible.name,
              collectibleIcon: collectible.icon,
              earnedAt: new Date(collectible.earnedAt),
              isDisplayed: true,
            },
            update: {
              collectibleType: collectible.type,
              collectibleName: collectible.name,
              collectibleIcon: collectible.icon,
            },
          });
          restoredItems++;
        }
      }

      // Log activity for analytics (but don't overwrite actual question attempts)
      console.log(`User ${userId} imported ${restoredItems} items from backup`);

      return {
        success: true,
        message: `Successfully restored ${restoredItems} items from your backup.`,
        restoredItems,
      };
    } catch (error) {
      console.error('Import error:', error);
      return {
        success: false,
        message: 'Failed to import data. Please try again.',
        restoredItems: 0,
      };
    }
  }

  /**
   * Generate download file for user
   */
  static generateDownloadFile(dataPackage: UserDataPackage): string {
    // Add checksum for verification
    const jsonString = JSON.stringify(dataPackage, null, 2);
    const checksum = this.generateChecksum(jsonString);
    
    return JSON.stringify({
      ...dataPackage,
      _checksum: checksum,
      _format: 'compex-user-data-v1',
    }, null, 2);
  }

  /**
   * Verify data integrity
   */
  static verifyDataIntegrity(dataPackage: UserDataPackage): boolean {
    if (dataPackage.version !== '1.0.0') return false;
    if (!dataPackage.user?.userid) return false;
    if (!dataPackage.exportedAt) return false;
    return true;
  }

  /**
   * Simple checksum for data verification
   */
  private static generateChecksum(data: string): string {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }
}

export default UserDataService;
