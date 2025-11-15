"""
Script to clear all calibrations from MongoDB
Run this to remove old calibration data with wrong format
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def clear_calibrations():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # Delete all calibrations
    result = await db.calibrations.delete_many({})
    
    print(f"✅ Deleted {result.deleted_count} calibration(s)")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    print("🗑️  Clearing all calibrations from database...")
    asyncio.run(clear_calibrations())
    print("✅ Done!")
