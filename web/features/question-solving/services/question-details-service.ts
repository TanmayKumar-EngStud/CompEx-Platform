import { prisma } from "@/shared/lib/configs/prisma";

/**
 * Service for fetching detailed question information
 * 
 * Handles retrieval of question details including options, metadata,
 * and parent problem set information for child questions.
 */

/**
 * Detailed question data with options and metadata
 */
export interface QuestionDetails {
   type: string;
   problemid: number;
   title: string;
   text: string;
   options_type: string | null;
   metadata: any;
   isChildren: boolean;
   problemsSetId: number | null;
   difficulty: number | null;
   addedDate: Date | null;
   problemoptions: {
      optiontext: string;
      iscorrect: boolean;
      group: string | null;
   }[];
   problemtags: {
      tags: {
         tagid: number;
         topic: string | null;
         theme: string | null;
         type: string | null;
         name: string | null;
      };
   }[];
   parentTags?: string[];
}

/**
 * Fetches detailed information for multiple questions
 * 
 * Retrieves question text, options, metadata, and handles special cases:
 * - For child questions, fetches parent problem set information (Optimized batching)
 * - For NE (Numeric Entry) questions, clears metadata to hide answers
 * 
 * @param questionIds - Array of question IDs to fetch details for
 * @returns Promise resolving to array of detailed question data
 */
export async function getQuestionDetails(questionIds: number[]): Promise<QuestionDetails[]> {
   // Fetch questions with optimized select
   const questions = await prisma.problems.findMany({
      where: {
         problemid: {
            in: questionIds,
         },
      },
      select: {
         type: true,
         problemid: true,
         title: true,
         text: true,
         options_type: true,
         metadata: true,
         isChildren: true,
         problemsSetId: true,
         difficulty: true,
         addedDate: true,
         problemoptions: {
            select: {
               optiontext: true,
               iscorrect: true,
               group: true,
            },
            orderBy: {
               optionid: "asc",
            },
         },
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

   // Performance Optimization: Batch fetch parent problem sets for child questions
   const parentSetIds = Array.from(new Set(
      questions
         // eslint-disable-next-line
         .filter((q: any) => q.isChildren && q.problemsSetId)
         // eslint-disable-next-line
         .map((q: any) => q.problemsSetId as number)
   ));

   const parentSetsMap = new Map();
   if (parentSetIds.length > 0) {
      const parentSets = await prisma.problemsSet.findMany({
         where: {
            problemsSetId: { in: parentSetIds }
         },
         select: {
            problemsSetId: true,
            title: true,
            content: true,
            problemssettags: {
               select: {
                  tag_scopes: {
                     select: {
                        tags: {
                           select: {
                              name: true,
                           },
                        },
                     },
                  },
               },
            },
         },
      });
      // eslint-disable-next-line
      parentSets.forEach((ps: any) => parentSetsMap.set(ps.problemsSetId, ps));
   }

   // Process each question to handle special cases
   const processedQuestions = questions.map((questionRaw: any) => {
      const question = {
         ...questionRaw,
         problemtags: (questionRaw.problemtags || []).map((pt: any) => {
            const t = pt.tag_scopes?.tags;
            if (!t) return null;
            return {
               tags: {
                  tagid: t.tagid,
                  topic: t.category === 'topic' ? t.name : null,
                  theme: t.category === 'theme' ? t.name : null,
                  type: t.category === 'type' ? t.name : null,
                  name: t.name
               }
            };
         }).filter(Boolean)
      };
      // Procress types for normalization
      const qType = (question.type || "").toLowerCase();
      const isGI = qType === "gi" || qType === "graphic interpretation" || qType === "graphic information";

      // Handle child questions - use cached parent metadata
      if (question.isChildren && question.problemsSetId) {
         const parentProblem = parentSetsMap.get(question.problemsSetId);
         if (parentProblem) {
            // Extract parent tag names
            const pTags = (parentProblem.problemssettags || [])
               .map((pst: any) => pst.tag_scopes?.tags?.name)
               .filter(Boolean);
            question.parentTags = pTags;

            if (isGI) {
               // For GI, merge parent content but keep local metadata as priority
               const localMetadata = typeof question.metadata === 'string'
                  ? JSON.parse(question.metadata)
                  : (question.metadata || {});

               question.metadata = {
                  ...parentProblem,
                  ...localMetadata
               };
            } else {
               question.metadata = { ...parentProblem };
            }
         }
      }

      // Handle NE (Numeric Entry) questions - clear metadata to hide answers
      const lowerType = qType.toLowerCase().trim();
      if (lowerType === "ne" || lowerType === "numerical entry" || lowerType === "numeric entry") {
         question.metadata = {};
      }

      // broad metadata cleaning to remove "answer" fields if they exist (requested by user)
      if (question.metadata) {
         try {
            let meta = typeof question.metadata === 'string' ? JSON.parse(question.metadata) : question.metadata;

            // Helper to recursively remove keys
            const cleanMetadata = (obj: any) => {
               if (!obj || typeof obj !== 'object') return;

               if (Array.isArray(obj)) {
                  obj.forEach(cleanMetadata);
                  return;
               }

               // Remove sensitive keys
               delete obj.answer;
               delete obj.correctAnswer;
               delete obj.solution;

               // Recurse
               Object.values(obj).forEach(cleanMetadata);
            };

            cleanMetadata(meta);
            question.metadata = meta;
         } catch (e) {
            console.error("Failed to clean metadata for question:", question.problemid, e);
         }
      }

      return question as QuestionDetails;
   });

   return processedQuestions;
}