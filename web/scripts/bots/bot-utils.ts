import fs from 'fs';
import path from 'path';

/**
 * Bot Feedback Collector
 * Collects "thoughts" from our synthetic users during their runs.
 */
export const logBotFeedback = (persona: string, action: string, feedback: string, status: 'SUCCESS' | 'FAIL' | 'WARN') => {
  const logEntry = {
    timestamp: new Date().toISOString(),
    persona,
    action,
    feedback,
    status
  };

  const logPath = path.join(process.cwd(), 'scripts/bots/bot_feedback.log');
  fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  
  console.log(`[BOT][${status}] ${persona}: ${feedback}`);
};
