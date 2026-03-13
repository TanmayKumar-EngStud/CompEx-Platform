
import fs from 'fs';
import path from 'path';

export class TemplateEngine {
    private templateDir: string;
    private schemaDir: string;

    constructor() {
        this.templateDir = path.join(process.cwd(), 'scripts/automation/templates');
        this.schemaDir = path.join(process.cwd(), 'scripts/automation/templates/schemas');
    }

    public getSystemTemplate(name: string): string {
        const filePath = path.join(this.templateDir, 'system', `${name}.txt.template`);
        return fs.readFileSync(filePath, 'utf-8');
    }

    public getComponentTemplate(name: string): string {
        const filePath = path.join(this.templateDir, 'components', `${name}.txt.template`);
        return fs.readFileSync(filePath, 'utf-8');
    }

    public getSchema(name: string): any {
        const filePath = path.join(this.schemaDir, `${name}.json.schema`);
        return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    }

    public render(template: string, values: Record<string, any>): string {
        let rendered = template;
        for (const [key, value] of Object.entries(values)) {
            const placeholder = new RegExp(`{{${key}}}`, 'g');
            rendered = rendered.replace(placeholder, typeof value === 'object' ? JSON.stringify(value, null, 2) : value);
        }
        return rendered;
    }
}
