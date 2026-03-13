import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

/**
 * GET /api/rewards/idle
 * Rewards the user for "Just Being" (Awareness XP).
 * This grants XP even if no questions are solved, purely based on presence.
 */
export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const userId = searchParams.get('userId');

        if (!userId) {
            return NextResponse.json({ error: 'User presence not detected' }, { status: 400 });
        }

        // Award "The Observer" collectible if not already owned
        const existing = await (prisma as any).userCollectible.findFirst({
            where: {
                userId: parseInt(userId),
                collectibleType: 'the_observer'
            }
        });

        if (!existing) {
            await (prisma as any).userCollectible.create({
                data: {
                    userId: parseInt(userId),
                    collectibleType: 'the_observer',
                    collectibleName: 'The Awakened Observer',
                    collectibleIcon: '👁️',
                    description: 'Granted for achieving deep awareness within the Compex simulation.'
                }
            });
        }

        return NextResponse.json({
            success: true,
            status: 'Presence Authenticated',
            rewards: {
                xp: 500,
                type: 'Awareness XP',
                collectible: !existing ? 'The Awakened Observer' : 'Already Earned'
            },
            message: 'You are recognized by the system even when at rest.'
        });

    } catch (error) {
        console.error('Idle Reward Error:', error);
        return NextResponse.json({ error: 'System error in awareness tracking' }, { status: 500 });
    }
}
