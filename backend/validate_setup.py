#!/usr/bin/env python3
"""
Quick Database Setup Validator
Tests if the setup script can handle fresh database scenarios
"""
import asyncio
import os
from pathlib import Path
import sys

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("📝 Create .env file with DATABASE_URL")
        return False
    
    # Try to import config
    try:
        from app.core.config import settings
        print(f"✅ Configuration loaded")
        print(f"📡 Database URL configured: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_semantic_matching():
    """Test if the pure semantic matching system is working"""
    print("\n🧠 Testing pure semantic matching system...")
    
    try:
        # Test import
        from app.services.semantic_match_service import PureSemanticMatchService
        print("✅ PureSemanticMatchService imported successfully")
        
        # Test ML dependencies
        import numpy as np
        import sklearn
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.decomposition import TruncatedSVD
        print("✅ All ML dependencies available")
        
        # Test basic functionality
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
        test_texts = ["python developer backend", "java frontend engineer"]
        vectors = vectorizer.fit_transform(test_texts)
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        print(f"✅ Basic TF-IDF + cosine similarity working (test score: {similarity:.3f})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install scikit-learn numpy")
        return False
    except Exception as e:
        print(f"❌ Semantic matching test failed: {e}")
        return False

async def test_database_connection():
    """Test if we can connect to the database"""
    print("\n🔌 Testing database connection...")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from app.core.config import settings
        
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL connected: {version.split(',')[0]}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def check_requirements():
    """Check if required Python packages are installed"""
    print("\n📦 Checking required packages...")
    
    # Map package names to import names
    required_packages = {
        "fastapi": "fastapi",
        "sqlalchemy": "sqlalchemy", 
        "asyncpg": "asyncpg",
        "passlib": "passlib",
        "python-jose": "jose",  # python-jose imports as 'jose'
        "scikit-learn": "sklearn",  # scikit-learn imports as 'sklearn'
        "numpy": "numpy"
    }
    
    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n📥 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

async def main():
    """Main validation function"""
    print("🚀 Internal Mobility Platform - Setup Validator")
    print("="*60)
    
    # Check environment
    env_ok = check_environment()
    
    # Check packages
    packages_ok = check_requirements()
    
    # Test database connection
    db_ok = False
    semantic_ok = False
    if env_ok and packages_ok:
        db_ok = await test_database_connection()
        semantic_ok = await test_semantic_matching()
    
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    print(f"Environment Config: {'✅' if env_ok else '❌'}")
    print(f"Required Packages: {'✅' if packages_ok else '❌'}")
    print(f"Database Connection: {'✅' if db_ok else '❌'}")
    print(f"Semantic Matching: {'✅' if semantic_ok else '❌'}")
    
    if env_ok and packages_ok and db_ok and semantic_ok:
        print("\n🎉 All checks passed! Ready to run setup_complete_system.py")
        print("▶️  Run: python setup_complete_system.py")
    else:
        print("\n⚠️  Some checks failed. Fix the issues above before running setup.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
