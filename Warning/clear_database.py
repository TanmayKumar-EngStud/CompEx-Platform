from prisma import Prisma

def main():
    prisma = Prisma()
    prisma.connect()

    print("Deleting User Attempts...")
    # Synchronous calls
    if hasattr(prisma, 'userattempt_selectedoptions'):
        prisma.userattempt_selectedoptions.delete_many()
    if hasattr(prisma, 'userattempts'):
        prisma.userattempts.delete_many()
    if hasattr(prisma, 'usermocktestattempts'):
        prisma.usermocktestattempts.delete_many()
    
    print("Deleting Questions and Analytics...")
    if hasattr(prisma, 'problemtags'):
        prisma.problemtags.delete_many()
    if hasattr(prisma, 'problemoptions'):
        prisma.problemoptions.delete_many()
    
    # Cascade delete might handle problemtags/options but explicit is safe
    if hasattr(prisma, 'problems'):
        prisma.problems.delete_many()
    
    if hasattr(prisma, 'analytics'):
        prisma.analytics.delete_many()

    print("Database cleared successfully.")
    prisma.disconnect()

if __name__ == '__main__':
    main()
