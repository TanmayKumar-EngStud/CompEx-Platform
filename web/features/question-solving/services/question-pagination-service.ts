import { prisma } from "@/shared/lib/configs/prisma";

/**
 * Service for handling question pagination and filtering
 * 
 * Manages the complex logic of fetching problems and problem sets
 * with user attempt data for pagination display.
 */

/**
 * Interface for paginated problem data
 */
export interface PaginatedProblemData {
   problemData: (ProblemWithAttempt | ProblemSetWithAttempts)[];
   totalProblems: number;
}

/**
 * Individual problem with user attempt status
 */
export interface ProblemWithAttempt {
   problemid: number;
   title: string;
   difficulty: number | null;
   addedDate: Date | null;
   type: string | null;
   problemsSetId: number | null;
   iscorrect: boolean | null;
   problemtags?: {
      tags: {
         tagid: number;
         topic: string | null;
         theme: string | null;
         type: string | null;
         name?: string | null; // Optional fallback
      }
   }[];
}

/**
 * Problem set with child problems and user attempt status
 */
export interface ProblemSetWithAttempts {
   problemsSetId: number;
   title: string;
   isExpanded: boolean;
   problems: ProblemWithAttempt[];
}

/**
 * Fetches problems and problem sets for pagination with user attempt data
 * 
 * This function handles complex filtering by exam type, section, and tags,
 * while efficiently fetching user attempt data for all problems.
 * 
 * @param userId - The ID of the user to fetch attempts for
 * @param examType - The exam type ID to filter by
 * @param section - The section ID to filter by
 * @param tags - Optional array of tag names to filter by
 * @returns Promise resolving to paginated problem data with attempt status
 */
export async function getProblemsForPagination(
   userId: number,
   examType: number,
   section: number | number[],
   filters: { topics?: string[] | null, themes?: string[] | null, types?: string[] | null } = {}
): Promise<PaginatedProblemData> {
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

   // Fetch top-level problems with optimized query
   const problemsRaw: any = await prisma.problems.findMany({
      where: {
         examtypeid: examType,
         sectionid: Array.isArray(section) ? { in: section } : section,
         isChildren: false,
         isMockQuestion: false,
         type: {
            not: "",
         },
         ...(hasFilters
            ? {
               problemtags: {
                  some: {
                     OR: tagFilter,
                  },
               },
            }
            : {}),
      },
      select: {
         problemid: true,
         title: true,
         difficulty: true,
         addedDate: true,
         type: true,
         problemsSetId: true,
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

   // Map raw problems to expected structure (flatten tag_scopes)
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


   // Fetch problem sets with child problems
   const problemSetsRaw: any = await prisma.problemsSet.findMany({
      where: {
         examtypeid: examType,
         sectionid: Array.isArray(section) ? { in: section } : section,
         mocksectionid: null,
         ...(hasFilters
            ? {
               OR: [
                  {
                     problems: {
                        some: {
                           problemtags: {
                              some: {
                                 OR: tagFilter,
                              },
                           },
                        },
                     },
                  },
                  {
                     problemssettags: {
                        some: {
                           OR: tagFilter,
                        },
                     },
                  },
               ],
            }
            : {}),
      },
      select: {
         problemsSetId: true,
         title: true,
         problems: {
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
                                 name: true, // was topic
                                 category: true, // was theme
                                 // type: true, // removed, implied by category
                                 // category: true, // category was in schema but not in original select, keeping it consistent
                              },
                           },
                        },
                     },
                  },
               },
            },
         },
      },
   } as any);

   const problemSets = problemSetsRaw.map((ps: any) => ({
      ...ps,
      problems: ps.problems.map((p: any) => ({
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
      }))
   }));

   // Collect all problem IDs for user attempts query
   const allProblemIds = [
      ...problems.map((p: any) => p.problemid),
      ...problemSets.flatMap((ps: any) => ps.problems.map((p: any) => p.problemid)),
   ];

   // Fetch user attempts efficiently
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

   // Create lookup map for O(1) attempt status retrieval
   const problemStatusMap = new Map(
      // eslint-disable-next-line
      userAttempts.map((attempt: any) => [attempt.problemid, attempt.iscorrect])
   );

   // Enrich problems with attempt status
   const enrichedProblems: ProblemWithAttempt[] = problems.map((problem: any) => ({
      ...problem,
      iscorrect: problemStatusMap.get(problem.problemid) ?? null,
   }));

   // Enrich problem sets with attempt status for child problems
   const enrichedProblemSets: ProblemSetWithAttempts[] = problemSets
      .map((problemSet: any) => {
         const enrichedChildProblems = problemSet.problems.map((childProblem: any) => ({
            ...childProblem,
            problemsSetId: problemSet.problemsSetId,
            iscorrect: problemStatusMap.get(childProblem.problemid) ?? null,
         }));

         return {
            problemsSetId: problemSet.problemsSetId,
            title: problemSet.title,
            isExpanded: false,
            problems: enrichedChildProblems,
         };
      })
      .filter((ps: ProblemSetWithAttempts) => ps.problems.length > 0);

   // Combine and sort by date
   const combinedProblemData = [...enrichedProblems, ...enrichedProblemSets];
   combinedProblemData.sort((a, b) => {
      const dateA = getComparisonDate(a);
      const dateB = getComparisonDate(b);
      return dateA.getTime() - dateB.getTime();
   });

   const totalProblems = problems.length + problemSets.length;

   return { problemData: combinedProblemData, totalProblems };
}

/**
 * Helper function to get comparison date for sorting
 * 
 * @param item - Problem or problem set to extract date from
 * @returns Date object for comparison
 */
function getComparisonDate(item: ProblemWithAttempt | ProblemSetWithAttempts): Date {
   if ("addedDate" in item && item.addedDate) {
      return new Date(item.addedDate);
   }

   if ("problems" in item && item.problems[0]?.addedDate) {
      return new Date(item.problems[0].addedDate);
   }

   return new Date(0); // Fallback to epoch
}