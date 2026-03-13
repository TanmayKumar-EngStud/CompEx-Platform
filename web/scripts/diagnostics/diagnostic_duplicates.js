
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

async function main() {
    const scopes = await prisma.tag_scopes.findMany({
        include: {
            tags: true,
            sections: true
        }
    });

    const groups = {};
    scopes.forEach(s => {
        const key = `${s.tags.name}|${s.sections.name}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(s.tagScopeId);
    });

    const duplicates = Object.entries(groups).filter(([k, ids]) => ids.length > 1);
    console.log("Found", duplicates.length, "duplicate tag/section combinations.");
    console.log(JSON.stringify(duplicates.slice(0, 10), null, 2));
}

main().catch(console.error).finally(() => prisma.$disconnect());
