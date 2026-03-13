import { prisma } from "@/shared/lib/configs/prisma";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";

export async function getTags(examtypeid: number, sectionid: number | number[]) {
   const tagScopes = await (prisma as any).tag_scopes.findMany({
      where: {
         examtypeid: examtypeid,
         sectionid: Array.isArray(sectionid) ? { in: sectionid } : sectionid,
      },
      include: {
         tags: true,
         problemtags: {
            include: {
               problems: {
                  select: {
                     isChildren: true,
                     problemsSetId: true,
                     isMockQuestion: true,
                  },
               },
            },
         },
         problemssettags: {
            include: {
               ProblemsSet: {
                  select: {
                     problemsSetId: true,
                     mocksectionid: true,
                  },
               },
            },
         },
      },
   });

   const tag: Tag[] = tagScopes
      .filter((scope: any) => scope.tags.name && scope.tags.name.trim() !== "")
      .map((scope: any) => {
         const { tags, problemtags, problemssettags } = scope;

         // Set of problemSetIds that have this tag (either directly or via children)
         const problemSetIds = new Set<number>();

         // ProblemSetIds from direct tags on ProblemSet
         (problemssettags || []).forEach((pst: any) => {
            if (pst.ProblemsSet && pst.ProblemsSet.mocksectionid === null) {
               problemSetIds.add(pst.problemsSetId);
            }
         });

         // Independent problems with this tag
         let independentProblemCount = 0;

         (problemtags || []).forEach((pt: any) => {
            const problem = pt.problems;
            if (problem && !problem.isMockQuestion) {
               if (problem.isChildren && problem.problemsSetId) {
                  // If it's a child with this tag, the whole set counts
                  problemSetIds.add(problem.problemsSetId);
               } else if (!problem.isChildren) {
                  // Independent problem
                  independentProblemCount++;
               }
            }
         });

         const totalCount = independentProblemCount + problemSetIds.size;

         const item = {
            tagid: tags.tagid,
            topic: tags.category === "topic" ? tags.name : null,
            theme: tags.category === "theme" ? tags.name : null,
            type: tags.category === "type" ? tags.name : null,
            name: tags.name,
            examtypeid: examtypeid,
            sectionid: Array.isArray(sectionid) ? sectionid[0] : sectionid,
            count: totalCount,
            isActive: false,
         };
         if (item.count === 152 || tags.name === "152" || !tags.name) {
            console.log("DEBUG: Suspicious Tag found:", item);
         }
         return item;
      })
      .filter((item: Tag) => item.count > 0);

   console.log(`getTags returning ${tag.length} tags for section ${sectionid}`);
   return tag;
}