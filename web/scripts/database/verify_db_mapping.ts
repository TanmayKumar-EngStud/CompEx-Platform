import { prisma } from "../shared/lib/configs/prisma";

async function main() {
    console.log("--- EXAM TYPES ---");
    const examTypes = await prisma.examtypes.findMany();
    console.log(examTypes);

    console.log("\n--- SECTIONS ---");
    const sections = await prisma.sections.findMany();
    console.log(sections);

    console.log("\n--- TAG SAMPLES (First 5) ---");
    const tags = await prisma.tags.findMany({ take: 5 });
    console.log(tags);

    console.log("\n--- SECTION ID SAMPLE ---");
    // Check which sections have what kind of tags
    const greQuantsTags = await (prisma as any).tag_scopes.findMany({
        where: { examtypeid: 2, sectionid: 4 },
        include: { tags: true },
        take: 5
    });
    console.log("Exam 2, Section 4 tags:", greQuantsTags.map((t: any) => t.tags.name));

    const greVerbalTags = await (prisma as any).tag_scopes.findMany({
        where: { examtypeid: 2, sectionid: 5 },
        include: { tags: true },
        take: 5
    });
    console.log("Exam 2, Section 5 tags:", greVerbalTags.map((t: any) => t.tags.name));
}

main().catch(console.error);
