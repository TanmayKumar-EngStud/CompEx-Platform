import { prisma } from "../shared/lib/configs/prisma";

async function main() {
    console.log("--- Sections ---");
    const sections = await prisma.sections.findMany({
        select: { sectionid: true, name: true, examtypeid: true }
    });
    console.log(sections);

    console.log("\n--- Tag Mapping for GRE Quants (Section 5) ---");
    // Assuming 2 is GRE, 5 is Quants based on current route logic
    const tagScopes = await (prisma as any).tag_scopes.findMany({
        where: {
            examtypeid: 2,
            sectionid: 5
        },
        include: {
            tags: true
        },
        take: 10
    });
    console.log("Sample tags for GRE Quants:", tagScopes.map((ts: any) => ({
        name: ts.tags.name,
        category: ts.tags.category
    })));

    console.log("\n--- Tag Mapping for GRE Verbal (Section 4) ---");
    const tagScopesVerbal = await (prisma as any).tag_scopes.findMany({
        where: {
            examtypeid: 2,
            sectionid: 4
        },
        include: {
            tags: true
        },
        take: 10
    });
    console.log("Sample tags for GRE Verbal:", tagScopesVerbal.map((ts: any) => ({
        name: ts.tags.name,
        category: ts.tags.category
    })));
}

main().catch(console.error);
