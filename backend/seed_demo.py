"""Seed demo workspace and API key"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.db.models import Workspace, Application, APIKey
from app.utils.crypto import generate_api_key, hash_api_key, get_key_prefix


def seed_demo_data():
    """Create demo workspace, application, and API key"""
    # Create tables first
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if demo workspace exists
        workspace = db.query(Workspace).filter(Workspace.slug == "demo").first()
        if workspace:
            print("Demo workspace already exists")
            return
        
        # Create workspace
        workspace = Workspace(
            name="Demo Workspace",
            slug="demo",
        )
        db.add(workspace)
        db.flush()
        
        # Create application
        application = Application(
            workspace_id=workspace.id,
            name="Demo Application",
            description="Demo application for testing",
        )
        db.add(application)
        db.flush()
        
        # Generate API key
        api_key = generate_api_key()
        db_api_key = APIKey(
            application_id=application.id,
            key_hash=hash_api_key(api_key),
            key_prefix=get_key_prefix(api_key),
            permissions="[]",
        )
        db.add(db_api_key)
        db.commit()
        
        print("=" * 60)
        print("Demo workspace created!")
        print("=" * 60)
        print(f"Workspace: {workspace.name} ({workspace.slug})")
        print(f"Application: {application.name}")
        print(f"API Key: {api_key}")
        print("=" * 60)
        print("SAVE THIS API KEY - it will not be shown again!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding demo data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
