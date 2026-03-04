import asyncio
import asyncpg
from backend.app.core.config import settings

async def test_connection():
    try:
        # Parse the DATABASE_URL
        db_url = settings.DATABASE_URL
        print(f"Testing connection to: {db_url}")
        
        # Try to connect
        conn = await asyncpg.connect(
            host="localhost",
            user="postgres",
            password="qwertyuiop",
            database="postgres" # Connect to default postgres database first
        )
        
        # Check if caption_db exists
        result = await conn.fetch(
            "SELECT 1 FROM pg_database WHERE datname='caption_db'"
        )
        
        if not result:
            print("Database 'caption_db' does not exist. Creating it...")
            await conn.execute('CREATE DATABASE caption_db')
            print("Database 'caption_db' created successfully!")
        else:
            print("Database 'caption_db' already exists.")
        
        await conn.close()
        
        # Now test connection to caption_db
        conn = await asyncpg.connect(
            host="localhost",
            user="postgre",
            password="qwertyuiop",
            database="caption_db"
        )
        print("Successfully connected to caption_db!")
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
