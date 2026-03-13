import { PrismaClient } from "@prisma/client";

declare global {
   var prisma: PrismaClient | undefined;
}

export const prisma = global.prisma || new PrismaClient();

if (process.env.NODE_ENV !== "production") {
   global.prisma = prisma;
}

// cleanup on shutdown - use a more robust way to prevent multiple listeners in dev
if (process.env.NODE_ENV !== "production") {
   // In dev, we don't want to keep adding listeners on HMR
} else {
   process.on("beforeExit", async () => {
      if (prisma) {
         await prisma.$disconnect();
      }
   });
}
