#!/usr/bin/env python3
"""
Dependency checker for DebtBot AI
"""
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"✅ {package_name} is installed")
            return True
        else:
            print(f"❌ {package_name} is not installed")
            return False
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False

def check_external_services():
    """Check external service connectivity"""
    import asyncio
    import httpx
    
    async def check_service(name, url):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"✅ {name} is accessible")
                    return True
                else:
                    print(f"⚠️ {name} returned status {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ {name} is not accessible: {e}")
            return False
    
    async def run_checks():
        # Check WhatsApp API
        await check_service(
            "WhatsApp API", 
            "https://graph.facebook.com/v18.0/me"
        )
        
        # Check if PostgreSQL is running (if using local)
        try:
            import asyncpg
            conn = await asyncpg.connect(
                "postgresql://postgres:password@localhost:5432/debtbot"
            )
            await conn.close()
            print("✅ PostgreSQL database is accessible")
        except Exception as e:
            print(f"⚠️ PostgreSQL database: {e}")
        
        # Check Redis
        try:
            import redis.asyncio as redis
            client = redis.from_url("redis://localhost:6379")
            await client.ping()
            await client.close()
            print("✅ Redis is accessible")
        except Exception as e:
            print(f"⚠️ Redis: {e}")
    
    asyncio.run(run_checks())

def main():
    """Main dependency check"""
    print("🔍 Checking DebtBot AI dependencies...\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking Python packages...")
    
    # Core packages
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("asyncpg", "asyncpg"),
        ("redis", "redis"),
        ("httpx", "httpx"),
        ("pydantic", "pydantic"),
        ("openai", "openai"),
        ("googletrans", "googletrans"),
        ("langdetect", "langdetect")
    ]
    
    missing_packages = []
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n🌐 Checking external services...")
    check_external_services()
    
    print("\n🎉 All dependencies checked!")
    print("You can now run: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
