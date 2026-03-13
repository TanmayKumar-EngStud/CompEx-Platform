import { prisma } from "../../../shared/lib/configs/prisma";

export interface ExploreTag {
    tagid: number;
    name: string;
    category: string;
    count: number;
    examName: string;
    sectionName: string;
}

export async function getExploreData() {
    const scopes = await prisma.tag_scopes.findMany({
        include: {
            tags: true,
            examtypes: true,
            sections: true,
            _count: {
                select: {
                    problemtags: true,
                    problemssettags: true
                }
            }
        }
    });

    // We use a Map to deduplicate tags that might appear multiple times due to 
    // duplicate exam/section names in the database.
    const uniqueTagsMap = new Map<string, ExploreTag>();

    // eslint-disable-next-line
    scopes.forEach((scope: any) => {
        const count = scope._count.problemtags + scope._count.problemssettags;
        if (count === 0) return;

        // Key based on the visual context of the user
        const key = `${scope.tags.name}-${scope.tags.category}-${scope.examtypes.name}-${scope.sections.name}`;

        const existing = uniqueTagsMap.get(key);
        if (existing) {
            existing.count += count;
        } else {
            uniqueTagsMap.set(key, {
                tagid: scope.tags.tagid,
                name: scope.tags.name,
                category: scope.tags.category,
                count: count,
                examName: scope.examtypes.name,
                sectionName: scope.sections.name
            });
        }
    });

    return Array.from(uniqueTagsMap.values());
}
