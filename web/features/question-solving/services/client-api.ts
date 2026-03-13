"use client";

/**
 * Client-side API service for question attempts
 * 
 * This file is completely isolated from server-side code and Prisma
 * to prevent any bundling issues that could cause Prisma to be included
 * in the client bundle.
 */

export interface ClientAttemptData {
  problemId: number;
  option: string[];
  timetaken: string | null;
  partialcorrectnessscore: number | null;
}

export interface ClientAttemptSubmission {
  userId: number;
  Attempt: ClientAttemptData[];
}

export interface ClientAttemptResult {
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
}

/**
 * Submit user attempts via API route (client-side only)
 * 
 * This function is guaranteed to only run on the client and makes
 * HTTP requests to the API routes, never calling Prisma directly.
 */
export async function submitAttemptClient(data: ClientAttemptSubmission): Promise<ClientAttemptResult[]> {
  console.log("🟢 CLIENT-API: submitAttemptClient function called!");
  console.log("🟢 CLIENT-API: This should be the ONLY function called!");
  console.log("🟢 CLIENT-API: Data received =", data);
  
  // Transform data format to match API expectations
  const transformedData = {
    userID: data.userId, // API expects userID, not userId
    Attempt: data.Attempt?.map(attempt => ({
      questionID: attempt.problemId, // API expects questionID, not problemId
      option: attempt.option,
      timetaken: attempt.timetaken,
      partialcorrectnessscore: attempt.partialcorrectnessscore,
    })) || [],
  };
  
  try {
    const response = await fetch("/api/problems/returnAttempt", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(transformedData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error submitting attempt:", error);
    throw error;
  }
}