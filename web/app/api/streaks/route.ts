import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
   try {
      const { searchParams } = request.nextUrl;
      const userIdStr = searchParams.get("userId");
      const userId = userIdStr ? parseInt(userIdStr) : null;

      if (!userId || userId === 0) {
         return NextResponse.json({
            currentstreak: 0,
            solvedToday: false,
            totalDays: 0,
         });
      }

      // Performance optimization: Get only the most recent N attempts. 
      // For streak calculation, 100 items is usually plenty (covers ~3 months of daily practice).
      const attempts = await prisma.userattempts.findMany({
         where: { userid: userId },
         select: { attemptdate: true },
         orderBy: { attemptdate: "desc" },
         take: 100
      });

      if (attempts.length === 0) {
         return NextResponse.json({
            currentstreak: 0,
            solvedToday: false,
            totalDays: 0,
         });
      }

      // Normalize dates to YYYY-MM-DD in local time
      const uniqueDatesSet = new Set<string>();
      // eslint-disable-next-line
      attempts.forEach((attempt: any) => {
         if (attempt.attemptdate) {
            const date = new Date(attempt.attemptdate);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            uniqueDatesSet.add(`${year}-${month}-${day}`);
         }
      });

      const uniqueDates = Array.from(uniqueDatesSet).sort().reverse();

      const today = new Date();
      const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

      // Check if user solved today
      const solvedToday = uniqueDates.includes(todayStr);

      // Calculate current streak
      let currentStreak = 0;
      let checkDate = new Date(today);

      // If user hasn't solved today, start checking from yesterday
      if (!solvedToday) {
         checkDate.setDate(checkDate.getDate() - 1);
      }

      // Count consecutive days backwards
      while (true) {
         const dStr = `${checkDate.getFullYear()}-${String(checkDate.getMonth() + 1).padStart(2, '0')}-${String(checkDate.getDate()).padStart(2, '0')}`;
         if (uniqueDates.includes(dStr)) {
            currentStreak++;
            checkDate.setDate(checkDate.getDate() - 1);
         } else {
            break;
         }
      }

      return NextResponse.json({
         currentstreak: currentStreak,
         solvedToday: solvedToday,
         totalDays: uniqueDates.length, // Note: this is capped at 100 for perf, which is fine for current UI needs
      });
   } catch (error) {
      console.error("Error fetching user streak:", error);
      return NextResponse.json(
         { error: "Failed to fetch user streak" },
         { status: 500 }
      );
   }
}
