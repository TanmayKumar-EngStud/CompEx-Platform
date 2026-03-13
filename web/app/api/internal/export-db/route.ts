import { NextResponse } from 'next/server';
import { prisma } from '@/shared/lib/configs/prisma';

export async function GET() {
    try {
        const data = {
            examTypes: await prisma.examtypes.findMany(),
            sections: await prisma.sections.findMany(),
            problemSets: await prisma.ProblemsSet.findMany(),
            problems: await prisma.problems.findMany(),
            options: await prisma.problemoptions.findMany(),
        };

        return NextResponse.json(data);
    } catch (error) {
        return NextResponse.json({ error: error instanceof Error ? error.message : String(error) }, { status: 500 });
    }
}
