
const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

async function main() {
    const tags = await prisma.tag_scopes.findMany({
        where: {
            tags: {
                name: {
                    contains: "Algebraic",
                    mode: 'insensitive'
                }
            }
        },
        include: {
            tags: true,
            sections: true
        }
    });

    console.log(JSON.stringify(tags.map(t => ({
        tagScopeId: t.tagScopeId,
        tagName: t.tags.name,
        sectionName: t.sections.name
    })), null, 2));
}

main().catch(console.error).finally(() => prisma.$disconnect());
