
import { prisma } from '../../shared/lib/prisma';
import fs from 'fs';
import path from 'path';

export const DEEPSEEK_TOOLS = [
    {
        type: "function",
        function: {
            name: "search_questions",
            description: "Search for existing questions in the database by topic, type, or difficulty to ensure diversity and avoid duplicates.",
            parameters: {
                type: "object",
                properties: {
                    topic: { type: "string", description: "The topic or keyword to search for (e.g., 'Algebra', 'Sentence Correction')" },
                    difficulty: { type: "number", description: "Difficulty level (1-5)" },
                    limit: { type: "number", description: "Max results to return", default: 5 }
                }
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_pool_stats",
            description: "Get broad statistics about the current question pool distribution across exams and sections.",
            parameters: {
                type: "object",
                properties: {}
            }
        }
    },
    {
        type: "function",
        function: {
            name: "read_source_file",
            description: "Read a specific source file from the project to understand current implementation details or component structure.",
            parameters: {
                type: "object",
                properties: {
                    file_path: { type: "string", description: "Relative path to the file (e.g., 'app/verify/page.tsx')" }
                },
                required: ["file_path"]
            }
        }
    },
    {
        type: "function",
        function: {
            name: "get_community_feedback",
            description: "Retrieve items from the community feedback log to prioritize improvements.",
            parameters: {
                type: "object",
                properties: {}
            }
        }
    }
];

export class DeepSeekToolkit {
    public async executeTool(name: string, args: any): Promise<string> {
        console.log(`🛠️ AI executing tool: ${name}`, args);

        try {
            switch (name) {
                case "search_questions":
                    return await this.searchQuestions(args);
                case "get_pool_stats":
                    return await this.getPoolStats();
                case "read_source_file":
                    return await this.readSourceFile(args.file_path);
                case "get_community_feedback":
                    return await this.getCommunityFeedback();
                default:
                    return `Error: Tool ${name} not found.`;
            }
        } catch (error: any) {
            console.error(`❌ Tool execution failed: ${name}`, error);
            return `Error executing tool: ${error.message}`;
        }
    }

    private async searchQuestions(args: any): Promise<string> {
        const { topic, difficulty, limit = 5 } = args;
        const questions = await prisma.problems.findMany({
            where: {
                OR: topic ? [
                    { title: { contains: topic, mode: 'insensitive' } },
                    { text: { contains: topic, mode: 'insensitive' } }
                ] : undefined,
                difficulty: difficulty || undefined
            },
            take: limit,
            select: {
                problemid: true,
                title: true,
                examtypes: { select: { name: true } },
                sections: { select: { name: true } }
            }
        });

        return JSON.stringify(questions);
    }

    private async getPoolStats(): Promise<string> {
        const stats = await prisma.problems.groupBy({
            by: ['difficulty'],
            _count: { problemid: true }
        });

        const examStats = await prisma.examtypes.findMany({
            include: {
                _count: { select: { problems: true } }
            }
        });

        return JSON.stringify({
            by_difficulty: stats,
            by_exam: examStats.map((e: any) => ({ name: e.name, count: e._count.problems }))
        });
    }

    private async readSourceFile(filePath: string): Promise<string> {
        const fullPath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);

        // Safety check: prevent path traversal
        if (!fullPath.startsWith(process.cwd())) {
            return "Error: Access denied (path traversal prevented).";
        }

        if (!fs.existsSync(fullPath)) {
            return "Error: File not found.";
        }

        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            return `Error: ${filePath} is a directory. Contents: ${fs.readdirSync(fullPath).join(', ')}`;
        }

        // Limit read size to avoid context bloat
        const content = fs.readFileSync(fullPath, 'utf-8');
        return content.length > 5000 ? content.substring(0, 5000) + "\n\n[...truncated due to size...]" : content;
    }

    private async getCommunityFeedback(): Promise<string> {
        const feedbackPath = path.join(process.cwd(), 'COMMUNITY_FEEDBACK.md');
        if (!fs.existsSync(feedbackPath)) {
            return "Error: COMMUNITY_FEEDBACK.md not found.";
        }
        return fs.readFileSync(feedbackPath, 'utf-8');
    }
}
