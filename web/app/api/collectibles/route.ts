import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// POST /api/collectibles/generate - Generate AI collectible via Antigravity
export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { userId, collectibleType, collectibleName } = body;

        if (!userId || !collectibleType) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
        }

        // Generate collectible using Antigravity AI
        const antigravityPrompt = `
            Create a unique digital collectible/badge for a user who earned the "${collectibleName}" achievement on Compex (an AI-powered GRE/GMAT practice platform).
            
            Generate a creative, visually appealing badge design description and an emoji representation.
            
            Requirements:
            - Clean, modern design suitable for a study/prep platform
            - Should feel rewarding and motivating
            - Include subtle references to academic excellence or growth
            - Keep it simple and recognizable at small sizes
            
            Respond in this JSON format:
            {
              "name": "${collectibleName}",
              "emoji": "🎯",
              "description": "A brief inspiring description of what this badge represents",
              "designTips": "Brief visual design notes for a designer"
            }
        `;

        // Call Antigravity API (you'll need to add your Antigravity API key)
        const antigravityResponse = await fetch('https://api.antigravity.com/v1/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.ANTIGRAVITY_API_KEY}`
            },
            body: JSON.stringify({
                prompt: antigravityPrompt,
                model: 'creative',
                max_tokens: 500
            })
        });

        let collectibleData = {
            name: collectibleName,
            emoji: '🏆',
            description: `You earned the ${collectibleName} badge!`,
            designTips: 'Gold trophy design with study theme'
        };

        if (antigravityResponse.ok) {
            const aiResult = await antigravityResponse.json();
            try {
                collectibleData = JSON.parse(aiResult.text || aiResult.content);
            } catch (e) {
                console.log('Failed to parse AI response, using default');
            }
        }

        // Store collectible type definition
        const collectibleTypeRecord = await prisma.collectibleType.upsert({
            where: { type: collectibleType },
            update: {},
            create: {
                type: collectibleType,
                name: collectibleData.name,
                icon: collectibleData.emoji,
                description: collectibleData.description,
                triggerRule: JSON.stringify({ earned: true }),
                isActive: true
            }
        });

        // Award to user
        const userCollectible = await prisma.userCollectible.create({
            data: {
                userId: parseInt(userId),
                collectibleType,
                collectibleName: collectibleData.name,
                collectibleIcon: collectibleData.emoji,
                description: collectibleData.description
            }
        });

        return NextResponse.json({
            success: true,
            collectible: userCollectible,
            aiGenerated: {
                emoji: collectibleData.emoji,
                description: collectibleData.description
            }
        });

    } catch (error) {
        console.error('Error generating collectible:', error);
        return NextResponse.json({ error: 'Failed to generate collectible' }, { status: 500 });
    }
}

// GET /api/collectibles - Get user's collectibles
export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const userId = searchParams.get('userId');

        if (!userId) {
            return NextResponse.json({ error: 'User ID required' }, { status: 400 });
        }

        const collectibles = await prisma.userCollectible.findMany({
            where: { userId: parseInt(userId) },
            orderBy: { earnedAt: 'desc' }
        });

        const availableTypes = await prisma.collectibleType.findMany({
            where: { isActive: true },
            orderBy: { createdAt: 'desc' }
        });

        return NextResponse.json({
            earned: collectibles,
            available: availableTypes
        });

    } catch (error) {
        console.error('Error fetching collectibles:', error);
        return NextResponse.json({ error: 'Failed to fetch collectibles' }, { status: 500 });
    }
}
