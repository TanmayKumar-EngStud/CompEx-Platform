import { prisma } from "@/shared/lib/configs/prisma";


export async function getProblemsSetForPagination(
   userId: number,
   examType: number,
   section: number | number[],
   filters: { topics?: string[] | null, themes?: string[] | null, types?: string[] | null } = {}
): Promise<{ problemSetWithProblems: any[]; totalProblemSets: number }> {
   const { topics, themes, types } = filters;

   const tagFilter: any = [];
   if (topics && topics.length > 0) {
      tagFilter.push({ tag_scopes: { tags: { name: { in: topics }, category: 'topic' } } });
   }
   if (themes && themes.length > 0) {
      tagFilter.push({ tag_scopes: { tags: { name: { in: themes }, category: 'theme' } } });
   }
   if (types && types.length > 0) {
      tagFilter.push({ tag_scopes: { tags: { name: { in: types }, category: 'type' } } });
   }

   const hasFilters = tagFilter.length > 0;

   const whereClause = {
      examtypeid: examType,
      sectionid: Array.isArray(section) ? { in: section } : section,
      ...(hasFilters
         ? {
            problems: {
               some: {
                  problemtags: {
                     some: {
                        OR: tagFilter,
                     },
                  },
               },
            },
         }
         : {
            problems: {
               some: {},
            },
         }),
   };
   const problemSetData: any = await prisma.problemsSet.findMany({
      where: whereClause as any,
      select: {
         problemsSetId: true,
         title: true,
      },
   } as any);
   // Get all problems associated with each problem set
   const problemSetWithProblems = await Promise.all(
      problemSetData.map(async (problemSet: any) => {
         const problemsRaw: any = await prisma.problems.findMany({
            where: {
               problemsSetId: problemSet.problemsSetId,
            },
            select: {
               problemid: true,
               title: true,
               difficulty: true,
               addedDate: true,
               type: true,
               problemtags: {
                  select: {
                     tag_scopes: {
                        select: {
                           tags: {
                              select: {
                                 tagid: true,
                                 name: true,
                                 category: true,
                              },
                           },
                        },
                     },
                  },
               },
            },
         } as any);

         const problems = problemsRaw.map((p: any) => ({
            ...p,
            problemtags: p.problemtags.map((pt: any) => {
               const t = pt.tag_scopes.tags;
               return {
                  tags: {
                     tagid: t.tagid,
                     topic: t.category === 'topic' ? t.name : null,
                     theme: t.category === 'theme' ? t.name : null,
                     type: t.category === 'type' ? t.name : null,
                     name: t.name
                  }
               };
            })
         }));

         return {
            ...problemSet,
            problems,
         };
      })
   );

   const allProblemIds = problemSetWithProblems.flatMap((ps: any) =>
      ps.problems.map((p: any) => p.problemid)
   );

   const userAttempts = await prisma.userattempts.findMany({
      where: {
         userid: userId,
         problemid: {
            in: allProblemIds,
         },
      },
      select: {
         problemid: true,
         iscorrect: true,
      },
   });

   const problemDataMap = new Map(
      // eslint-disable-next-line
      userAttempts.map((attempt: any) => [attempt.problemid, attempt.iscorrect])
   );

   const problemSetWithProblemsAndStatus = problemSetWithProblems.map(
      (problemSet: any) => ({
         ...problemSet,
         problems: problemSet.problems.map((problem: any) => ({
            ...problem,
            iscorrect: problemDataMap.get(problem.problemid) ?? null,
         })),
      })
   );

   const totalProblemSets = await prisma.problemsSet.count({
      where: whereClause as any,
   });

   return {
      problemSetWithProblems: problemSetWithProblemsAndStatus,
      totalProblemSets,
   };
}