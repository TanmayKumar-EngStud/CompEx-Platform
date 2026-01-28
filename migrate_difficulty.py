import asyncio
import json
from db_artilaries import artilaries

DATA = {
    "GRE": [
        {
            "name": "Quants",
            "Quants": {
                "1": {"easy": 0.7, "medium": 0.2, "hard": 0.1},
                "2": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
                "3": {"easy": 0.5, "medium": 0.35, "hard": 0.15},
                "4": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
                "5": {"easy": 0.3, "medium": 0.4, "hard": 0.3}
            }
        },
        {
            "name": "Verbal",
            "Verbal": {
                "1": {"easy": 0.65, "medium": 0.25, "hard": 0.1},
                "2": {"easy": 0.55, "medium": 0.3, "hard": 0.15},
                "3": {"easy": 0.45, "medium": 0.35, "hard": 0.2},
                "4": {"easy": 0.35, "medium": 0.35, "hard": 0.3},
                "5": {"easy": 0.25, "medium": 0.35, "hard": 0.4}
            }
        },
        {
            "name": "Quants",
            "Quants": {
                "1": {"easy": 0.7, "medium": 0.2, "hard": 0.1},
                "2": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
                "3": {"easy": 0.5, "medium": 0.35, "hard": 0.15},
                "4": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
                "5": {"easy": 0.3, "medium": 0.4, "hard": 0.3}
            }
        },
        {
            "name": "Verbal",
            "Verbal": {
                "1": {"easy": 0.65, "medium": 0.25, "hard": 0.1},
                "2": {"easy": 0.55, "medium": 0.3, "hard": 0.15},
                "3": {"easy": 0.45, "medium": 0.35, "hard": 0.2},
                "4": {"easy": 0.35, "medium": 0.35, "hard": 0.3},
                "5": {"easy": 0.25, "medium": 0.35, "hard": 0.4}
            }
        }
    ],
    "GMAT": [
        {
            "name": "Integrated Reasoning",
            "Integrated Reasoning": {
                "1": {"easy": 0.7, "medium": 0.2, "hard": 0.1},
                "2": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
                "3": {"easy": 0.5, "medium": 0.35, "hard": 0.15},
                "4": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
                "5": {"easy": 0.3, "medium": 0.4, "hard": 0.3}
            }
        },
        {
            "name": "Quants",
            "Quants": {
                "1": {"easy": 0.7, "medium": 0.2, "hard": 0.1},
                "2": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
                "3": {"easy": 0.5, "medium": 0.35, "hard": 0.15},
                "4": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
                "5": {"easy": 0.3, "medium": 0.4, "hard": 0.3}
            }
        },
        {
            "name": "Verbal",
            "Verbal": {
                "1": {"easy": 0.65, "medium": 0.25, "hard": 0.1},
                "2": {"easy": 0.55, "medium": 0.3, "hard": 0.15},
                "3": {"easy": 0.45, "medium": 0.35, "hard": 0.2},
                "4": {"easy": 0.35, "medium": 0.35, "hard": 0.3},
                "5": {"easy": 0.25, "medium": 0.35, "hard": 0.4}
            }
        }
    ]
}

async def migrate():
    await artilaries.connect()
    print("Connected to DB.")
    
    key = "difficulty_distribution"
    content = json.dumps(DATA)
    
    # Check if exists
    existing = await artilaries._db.config.find_unique(where={'key': key})
    if existing:
        print(f"Updating existing key: {key}")
        await artilaries._db.config.update(
            where={'key': key},
            data={'content': content}
        )
    else:
        print(f"Creating new key: {key}")
        await artilaries._db.config.create(
            data={'key': key, 'content': content}
        )
    
    print("Migration complete.")
    await artilaries.disconnect()

if __name__ == "__main__":
    asyncio.run(migrate())
