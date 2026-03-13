import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

export async function GET(req: NextRequest) {
   try {
      const users = await prisma.users.findMany({
         select: {
            userid: true,
            username: true,
            email: true,
            image_url: true,
         } as any,
         orderBy: {
            userid: 'asc',
         },
      });
      return NextResponse.json(users);
   } catch (err) {
      console.error("Failed to fetch users:", err);
      return NextResponse.json(
         { message: "Failed to fetch users" },
         { status: 500 }
      );
   }
}
