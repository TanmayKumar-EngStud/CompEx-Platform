from prisma import Prisma

def main():
    print("Connecting to Prisma...")
    prisma = Prisma()
    try:
        prisma.connect()
        print("Connected successfully!")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Tip: Check your DATABASE_URL in .env. If running locally, ensure it uses 'localhost' instead of 'host.docker.internal'.")
        return

    print("Deleting User Attempts...")
    # Synchronous calls
    if hasattr(prisma, 'userattempt_selectedoptions'):
        prisma.userattempt_selectedoptions.delete_many()
    if hasattr(prisma, 'userattempts'):
        prisma.userattempts.delete_many()
    if hasattr(prisma, 'usermocktestattempts'):
        prisma.usermocktestattempts.delete_many()
    
    print("Deleting Questions and Analytics...")
    if hasattr(prisma, 'problemssettags'):
        prisma.problemssettags.delete_many()
    if hasattr(prisma, 'problemtags'):
        prisma.problemtags.delete_many()
    
    # Also delete the Tags definitions
    if hasattr(prisma, 'tags'):
        prisma.tags.delete_many()

    if hasattr(prisma, 'problemoptions'):
        prisma.problemoptions.delete_many()
    
    if hasattr(prisma, 'problems'):
        prisma.problems.delete_many()
    
    if hasattr(prisma, 'problemsset'):
        prisma.problemsset.delete_many()

    if hasattr(prisma, 'mocksections'):
        prisma.mocksections.delete_many()
    
    if hasattr(prisma, 'mocktests'):
        prisma.mocktests.delete_many()

    if hasattr(prisma, 'analytics'):
        prisma.analytics.delete_many()

    print("Database cleared successfully.")
    prisma.disconnect()
    
if __name__ == '__main__':
    main()