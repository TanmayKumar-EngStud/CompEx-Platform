import { NextRequest, NextResponse } from "next/server";
import { submitUserAttemptSERVER } from "@/features/question-solving/services/question-attempt-service";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const transformedBody = {
      userID: body.userID,
      Attempt: body.Attempt
    };
    const result = await submitUserAttemptSERVER(transformedBody);
    return NextResponse.json(result);
  } catch (error) {
    console.error("Submit API error:", error);
    return NextResponse.json({ error: "Failed to submit" }, { status: 500 });
  }
}