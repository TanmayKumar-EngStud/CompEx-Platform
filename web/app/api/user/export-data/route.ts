// API Route: Export User Data
// GET /api/user/export-data
// User can download all their data as JSON

import { NextRequest, NextResponse } from 'next/server';
import { jose } from '@/lib/jwt';
import UserDataService from '@/features/user-data/user-data-service';

export async function GET(request: NextRequest) {
  try {
    // Get user from token
    const token = request.cookies.get('token')?.value;
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const payload = await jose.jwtVerify(token);
    const userId = payload.userId as number;

    // Export all user data
    const dataPackage = await UserDataService.exportUserData(userId);

    // Generate downloadable file
    const jsonContent = UserDataService.generateDownloadFile(dataPackage);

    // Return as downloadable JSON
    return new NextResponse(jsonContent, {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="compex-data-${new Date().toISOString().split('T')[0]}.json"`,
        'Cache-Control': 'no-store',
      },
    });

  } catch (error) {
    console.error('Export error:', error);
    return NextResponse.json(
      { error: 'Failed to export data' },
      { status: 500 }
    );
  }
}
