import { prisma } from "@/shared/lib/configs/prisma";
import { UserAttempts } from "@/features/question-solving/hooks/(pagination)/problemDefinition";
import { parseTimeToSeconds } from "@/shared/lib/utils/formatting";

/**
 * Service for processing user question attempts
 * 
 * Handles submission of user answers, validation against correct answers,
 * and storage of attempt data with detailed results.
 */

/**
 * Interface for attempt submission result
 */
export interface AttemptResult {
   problemid: number;
   type: string;
   title: string | undefined;
   text: string | undefined;
   correctoption: string[];
   selectedoption: string[];
   timetaken: string;
   metadata: any;
   diagram: string | null;
   options: { optiontext: string; group: string | null }[] | undefined;
   solution: string | undefined;
   difficulty: string | undefined;
   options_type?: string | null;
   problemtags?: any[];
   parentTags?: string[];
}

/**
 * Interface for formatted attempt data
 */
interface FormattedAttemptData {
   type: string;
   problemId: number;
   correctAnswer: string[];
   selectedAttempt: string[];
   selectedoptionid: number[];
   timetaken: string;
   partialcorrectnessscore: number;
   metadata: any;
   difficulty?: number;
   problemtags?: any[];
}

/**
 * Interface for user attempt data for database storage
 */
interface UserAttemptData {
   userid: number;
   problemid: number;
   iscorrect: boolean;
   attemptdate: string;
   timetaken: string;
   partialcorrectnessscore: number;
   selectedoptionid: number[];
   difficulty?: number;
   problemtags?: any[];
}

/**
 * Submits user attempts and returns detailed results
 * 
 * This function processes user answers, validates them against correct answers,
 * stores the attempts in the database, and returns comprehensive result data
 * including solutions and explanations.
 * 
 * @param body - User attempt data containing answers and timing
 * @returns Promise resolving to detailed attempt results
 */
export async function submitUserAttemptSERVER(body: any): Promise<AttemptResult[]> {

   if (!body.Attempt || body.Attempt.length === 0) {
      return [];
   }

   // Fetch correct answers and question details
   const correctAnswersData = await prisma.problems.findMany({
      where: {
         problemid: {
            in: body.Attempt.map((attempt: any) => attempt.questionID || attempt.problemId),
         },
      },
      select: {
         type: true,
         problemid: true,
         title: true,
         text: true,
         options_type: true,
         problemsSetId: true,
         isChildren: true,
         difficulty: true,
         metadata: true,
         solution: true,
         problemoptions: {
            select: {
               optionid: true,
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
               tagScopeId: true,
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
   });

   // Enrich questions with parent metadata for child questions
   const enrichedQuestions = await enrichQuestionsWithParentData(correctAnswersData);

   // Format attempt data for processing
   const formattedData = formatAttemptData(enrichedQuestions, body);

   // Store attempts in database
   try {
      await storeUserAttempts(body.userID, formattedData);
   } catch (error) {
      console.error("Error storing user attempts:", error);
   }

   // Generate detailed results for display
   return generateAttemptResults(formattedData, enrichedQuestions);
}

/**
 * Enriches questions with parent problem set data for child questions
 * 
 * @param questions - Array of question data from database
 * @returns Promise resolving to enriched question data
 */
async function enrichQuestionsWithParentData(questions: any[]): Promise<any[]> {
   return Promise.all(
      // eslint-disable-next-line
      questions.map(async (question: any) => {
         // Handle child questions - fetch parent content
         if (question.isChildren && question.problemsSetId) {
            const parentProblemContent = await prisma.problemsSet.findFirst({
               where: {
                  problemsSetId: question.problemsSetId,
               },
               select: {
                  problemsSetId: true,
                  title: true,
                  type: true,
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

            if (parentProblemContent) {
               question.metadata = { ...parentProblemContent };
               question.parentTags = (parentProblemContent.problemssettags || [])
                  .map((pst: any) => pst.tag_scopes?.tags?.name)
                  .filter(Boolean);
            }
         }

         // Handle NE (Numeric Entry) questions - add answer as option
         if (
            question.type === "NE" &&
            question.metadata !== null &&
            typeof question.metadata === "object" &&
            "answer" in question.metadata
         ) {
            const answer = question.metadata.answer || "Not Found";
            question.problemoptions.push({
               optionid: -1,
               optiontext: answer.toString(),
               iscorrect: true,
               group: null,
            });
            delete question.metadata?.answer;
         }

         return question;
      })
   );
}

/**
 * Formats attempt data for processing and storage
 * 
 * @param questions - Enriched question data
 * @param body - User attempt submission data
 * @returns Array of formatted attempt data
 */
function formatAttemptData(questions: any[], body: UserAttempts): FormattedAttemptData[] {
   // eslint-disable-next-line
   return questions.map((question: any) => {
      // Extract correct answers
      const correctAnswer: string[] = question.problemoptions
         .filter((option: any) => option.iscorrect)
         .map((option: any) => option.optiontext);

      // Find user's attempt for this question
      const selectedAttempt = body.Attempt?.find(
         // eslint-disable-next-line
         (attempt: any) => ((attempt as any).questionID || (attempt as any).problemId) === question.problemid
      );

      // Map selected options to option IDs
      const selectedOptions: number[] = selectedAttempt?.option
         ? selectedAttempt.option
            .map((optText) => {
               const matchingOption = question.problemoptions.find(
                  (option: any) => option.optiontext === optText
               );
               return matchingOption?.optionid;
            })
            .filter((optionId) => optionId !== undefined) // Remove undefined values
         : [];

      return {
         type: question.type,
         problemId: question.problemid,
         correctAnswer,
         selectedAttempt: selectedAttempt?.option || ["not selected"],
         selectedoptionid: selectedOptions,
         timetaken: selectedAttempt?.timetaken || "0 sec",
         partialcorrectnessscore: selectedAttempt?.partialcorrectnessscore || 0,
         metadata: question.metadata,
         difficulty: question.difficulty,
         problemtags: question.problemtags,
      };
   });
}

/**
 * Stores user attempts in the database
 * 
 * @param userId - ID of the user making attempts
 * @param formattedData - Formatted attempt data to store
 */
async function storeUserAttempts(
   userId: number,
   formattedData: FormattedAttemptData[]
): Promise<void> {
   // Check for existing attempts to avoid duplicates
   const existingAttempts = await prisma.userattempts.findMany({
      where: {
         userid: userId,
         problemid: {
            in: formattedData.map(({ problemId }) => problemId),
         },
      },
      select: {
         userid: true,
         problemid: true,
      },
   });

   // Create lookup set for existing attempts
   const existingSet = new Set(
      existingAttempts.map(
         // eslint-disable-next-line
         (attempt: any) => `${attempt.userid}-${attempt.problemid}`
      )
   );

   // Filter out attempts that already exist
   const newAttempts: UserAttemptData[] = formattedData
      .filter(({ problemId }) => !existingSet.has(`${userId}-${problemId}`))
      .map(
         ({
            problemId,
            correctAnswer,
            selectedAttempt,
            selectedoptionid,
            timetaken,
            partialcorrectnessscore,
            problemtags,
         }) => ({
            userid: userId,
            problemid: problemId,
            iscorrect: areListsEqualIgnoringOrder(selectedAttempt, correctAnswer),
            attemptdate: new Date().toISOString(),
            timetaken,
            partialcorrectnessscore,
            selectedoptionid,
            difficulty:
               (formattedData.find((d) => d.problemId === problemId) as any)
                  ?.difficulty,
            problemtags,
         })
      );

   // Store new attempts
   if (newAttempts.length > 0) {
      for (const attempt of newAttempts) {
         // 1. Create user attempt record
         const createdAttempt = await prisma.userattempts.create({
            data: {
               userid: attempt.userid,
               problemid: attempt.problemid,
               attemptdate: attempt.attemptdate,
               timetaken: attempt.timetaken,
               partialcorrectnessscore: attempt.partialcorrectnessscore,
               iscorrect: attempt.iscorrect,
            },
         });

         const timeInSeconds = parseTimeToSeconds(attempt.timetaken);

         // 2. Store selected options (only if there are valid option IDs)
         if (attempt.selectedoptionid.length > 0) {
            const selectedOptions = attempt.selectedoptionid.map((optionId) => ({
               userattemptid: createdAttempt.attemptid,
               optionid: optionId,
            }));

            await prisma.userattempt_selectedoptions.createMany({
               data: selectedOptions,
            });
         }

         // 3. Update user_overall_performance (O(1))
         await (prisma as any).user_overall_performance.upsert({
            where: {
               userid_is_mock: {
                  userid: attempt.userid,
                  is_mock: false
               }
            },
            update: {
               total_attempts: { increment: 1 },
               total_correct: { increment: attempt.iscorrect ? 1 : 0 },
               total_incorrect: { increment: attempt.iscorrect ? 0 : 1 },
               correct_total_time: { increment: attempt.iscorrect ? timeInSeconds : 0 },
               incorrect_total_time: { increment: attempt.iscorrect ? 0 : timeInSeconds },
               last_updated: new Date()
            },
            create: {
               userid: attempt.userid,
               is_mock: false,
               total_attempts: 1,
               total_correct: attempt.iscorrect ? 1 : 0,
               total_incorrect: attempt.iscorrect ? 0 : 1,
               correct_total_time: attempt.iscorrect ? timeInSeconds : 0,
               incorrect_total_time: attempt.iscorrect ? 0 : timeInSeconds,
               last_updated: new Date()
            }
         });

         // 4. Update user_tag_performance (O(1) Skill Breakdown)
         if (attempt.problemtags && attempt.problemtags.length > 0) {
            for (const pt of attempt.problemtags) {
               const tagScopeId = pt.tagScopeId;
               if (tagScopeId) {
                  await (prisma as any).user_tag_performance.upsert({
                     where: {
                        userid_tagScopeId_is_mock: {
                           userid: attempt.userid,
                           tagScopeId: tagScopeId,
                           is_mock: false
                        }
                     },
                     update: {
                        total_attempts: { increment: 1 },
                        total_correct: { increment: attempt.iscorrect ? 1 : 0 },
                        total_time_seconds: { increment: timeInSeconds }
                     },
                     create: {
                        userid: attempt.userid,
                        tagScopeId: tagScopeId,
                        is_mock: false,
                        total_attempts: 1,
                        total_correct: attempt.iscorrect ? 1 : 0,
                        total_time_seconds: timeInSeconds
                     }
                  });
               }
            }
         }

         // 5. Update user_difficulty_stats (O(1) Difficulty Breakdown)
         if (attempt.difficulty) {
            await (prisma as any).user_difficulty_stats.upsert({
               where: {
                  userid_difficulty_is_mock: {
                     userid: attempt.userid,
                     difficulty: attempt.difficulty,
                     is_mock: false
                  }
               },
               update: {
                  total_attempts: { increment: 1 },
                  total_correct: { increment: attempt.iscorrect ? 1 : 0 },
                  total_time: { increment: timeInSeconds },
                  last_updated: new Date()
               },
               create: {
                  userid: attempt.userid,
                  difficulty: attempt.difficulty,
                  is_mock: false,
                  total_attempts: 1,
                  total_correct: attempt.iscorrect ? 1 : 0,
                  total_time: timeInSeconds,
                  last_updated: new Date()
               }
            });
         }
      }
   }
}

/**
 * Generates detailed results for display
 * 
 * @param formattedData - Formatted attempt data
 * @param questions - Original question data
 * @returns Array of detailed attempt results
 */
function generateAttemptResults(
   formattedData: FormattedAttemptData[],
   questions: any[]
): AttemptResult[] {
   return formattedData.map((attempt) => {
      const question = questions.find(
         (q) => q.problemid === attempt.problemId
      );

      if (!question) {
         throw new Error(`Question not found for problem ID: ${attempt.problemId}`);
      }

      const metadata = question.metadata as { diagram?: string } | null;
      const diagram = metadata?.diagram?.toString() ?? null;

      const options = question.problemoptions.map((option: any) => ({
         optiontext: option.optiontext,
         group: option.group,
      }));

      return {
         problemid: attempt.problemId,
         type: attempt.type,
         title: question.title,
         text: question.text,
         correctoption: attempt.correctAnswer,
         selectedoption: attempt.selectedAttempt,
         timetaken: attempt.timetaken,
         metadata: attempt.metadata,
         diagram,
         options,
         solution: question.solution,
         difficulty: question.difficulty,
         options_type: (question as any).options_type,
         problemtags: (question.problemtags || []).map((pt: any) => ({
            tags: pt.tag_scopes.tags,
         })),
         parentTags: question.parentTags || [],
      };
   });
}

/**
 * Utility function to compare arrays ignoring order
 * 
 * @param selectedAttempt - User's selected answers
 * @param correctAnswer - Correct answers
 * @returns True if arrays contain the same elements
 */
function areListsEqualIgnoringOrder(
   selectedAttempt: string[],
   correctAnswer: string[]
): boolean {
   if (!Array.isArray(selectedAttempt) || !Array.isArray(correctAnswer)) {
      return false;
   }

   if (selectedAttempt.length !== correctAnswer.length) {
      return false;
   }

   const sortedSelected = [...selectedAttempt].sort();
   const sortedCorrect = [...correctAnswer].sort();

   return sortedSelected.every((item, index) => item === sortedCorrect[index]);
}