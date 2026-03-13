// API Route: Import User Data
// POST /api/user/import-data
// User can upload their JSON to restore progress

import { NextRequest, NextResponse } from 'next/server';
import { jose } from '@/lib/jwt';
import UserDataService from '@/features/user-data/user-data-service';

export async function POST(request: NextRequest) {
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

    // Parse the uploaded file
    const body = await request.json();

    if (!body || !body._format || body._format !== 'compex-user-data-v1') {
      return NextResponse.json(
        {
          error: 'Invalid file format. Please upload a valid Compex data backup.',
          hint: 'The file must be exported from Compex app/website',
        },
        { status: 400 }
      );
    }

    // Verify data integrity
    if (!UserDataService.verifyDataIntegrity(body)) {
      return NextResponse.json(
        { error: 'Data verification failed. The file may be corrupted.' },
        { status: 400 }
      );
    }

    // Import the data
    const result = await UserDataService.importUserData(userId, body);

    if (!result.success) {
      return NextResponse.json(
        { error: result.message },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      message: result.message,
      restoredItems: result.restoredItems,
      note: 'Your learning progress has been restored. Some data may need time to sync.',
    });

  } catch (error) {
    console.error('Import error:', error);
    return NextResponse.json(
      { error: 'Failed to import data. Please try again.' },
      { status: 500 }
    );
  }
}
