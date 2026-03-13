
import { getTags } from '../features/exam-management/services/tag-queries';

async function main() {
    console.log("--- Debugging Tags for GRE Quants (Section 4, 7) ---");
    const tags = await getTags(2, [4, 7]);

    let anomalies: any[] = [];
    let totalCount = 0;

    tags.forEach(t => {
        totalCount += t.count;
        const debugInfo = {
            name: t.name,
            nameLen: t.name ? t.name.length : 'null',
            topic: t.topic,
            topicLen: t.topic ? t.topic.length : 'null',
            count: t.count,
            tagid: t.tagid
        };

        // Check for empty/whitespace topic/theme/type
        const isSuspicious =
            !t.name || t.name.trim().length === 0 ||
            (!t.topic && !t.theme && !t.type) ||
            (t.topic && t.topic.trim().length === 0) ||
            (t.topic === " ") ||
            (t.topic === "");

        if (isSuspicious || t.count === 152 || t.name === "152") {
            anomalies.push(debugInfo);
        }
    });

    console.log("Total Tags:", tags.length);
    console.log("Anomalies Found:", anomalies);
    console.log("Total Count sum:", totalCount);
}

main();
