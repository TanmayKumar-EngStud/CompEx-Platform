"use client";

interface SubmitData {
  userId: number;
  Attempt: Array<{
    problemId: number;
    option: string[];
    timetaken: string | null;
    partialcorrectnessscore: number | null;
  }>;
}

export async function submitAnswersAPI(data: SubmitData) {
  console.log("🟢 ISOLATED API CLIENT CALLED");
  
  const payload = {
    userID: data.userId,
    Attempt: data.Attempt.map(attempt => ({
      questionID: attempt.problemId,
      option: attempt.option,
      timetaken: attempt.timetaken,
      partialcorrectnessscore: attempt.partialcorrectnessscore,
    }))
  };

  try {
    const response = await fetch("/api/problems/returnAttempt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("🟢 API SUCCESS:", result);
    return result;
  } catch (error) {
    console.error("🔴 API ERROR:", error);
    throw error;
  }
}