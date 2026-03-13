
import fs from 'fs';
import path from 'path';

export class PhaseCache {
    private cacheDir: string;

    constructor() {
        this.cacheDir = path.join(process.cwd(), 'scripts/automation/.cache');
        if (!fs.existsSync(this.cacheDir)) {
            fs.mkdirSync(this.cacheDir, { recursive: true });
        }
    }

    private getCacheKey(scopeId: string, difficulty: number, phase: string): string {
        return path.join(this.cacheDir, `${scopeId}_d${difficulty}_${phase}.json`);
    }

    public get(scopeId: string, difficulty: number, phase: string): any | null {
        const filePath = this.getCacheKey(scopeId, difficulty, phase);
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            const oneHourAgo = Date.now() - (60 * 60 * 1000);
            if (stats.mtimeMs > oneHourAgo) {
                return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
            }
        }
        return null;
    }

    public set(scopeId: string, difficulty: number, phase: string, data: any): void {
        const filePath = this.getCacheKey(scopeId, difficulty, phase);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    }

    public clear(scopeId: string, difficulty: number): void {
        const phases = ['metadata', 'text', 'options', 'solution'];
        for (const phase of phases) {
            const filePath = this.getCacheKey(scopeId, difficulty, phase);
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }
        }
    }
}
