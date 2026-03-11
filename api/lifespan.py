from contextlib import asynccontextmanager
from sqlalchemy import text
from db.database import Base, engine


@asynccontextmanager
async def lifespan(app):
    print("\n" + "=" * 60)
    print("🚀 Starting Chatbox API")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  Application may not function correctly!")

    yield

    engine.dispose()
    print("👋 Chatbox API shutdown complete")
