
import * as dotenv from 'dotenv'
dotenv.config({ path: '.env.production', override: true })

async function listModels() {
    const key = process.env.GOOGLE_AI_STUDIO_KEY;
    if (!key) {
        console.error('No GOOGLE_AI_STUDIO_KEY found.');
        return;
    }

    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${key}`;
    console.log(`Checking models at: ${url.replace(key, '***')}`);

    try {
        const response = await fetch(url);
        const data: any = await response.json();

        if (data.error) {
            console.error('Error:', data.error);
        } else {
            console.log('Available Models:');
            data.models?.forEach((m: any) => {
                if (m.name.includes('gemini')) {
                    console.log(`- ${m.name} (${m.supportedGenerationMethods?.join(', ')})`);
                }
            });
        }
    } catch (e) {
        console.error('Fetch error:', e);
    }
}

listModels();
