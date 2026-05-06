# Test script to verify backend installation
import sys

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import fastapi
        print(f"[OK] FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"[FAIL] FastAPI: {e}")
        return False

    try:
        import uvicorn
        print(f"[OK] Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"[FAIL] Uvicorn: {e}")
        return False

    try:
        import motor
        version = getattr(motor, '__version__', 'installed')
        print(f"[OK] Motor: {version}")
    except ImportError as e:
        print(f"[FAIL] Motor: {e}")
        return False

    try:
        import pydantic
        print(f"[OK] Pydantic: {pydantic.__version__}")
    except ImportError as e:
        print(f"[FAIL] Pydantic: {e}")
        return False

    try:
        import httpx
        print(f"[OK] HTTPX: {httpx.__version__}")
    except ImportError as e:
        print(f"[FAIL] HTTPX: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Testing backend dependencies...")
    print("-" * 40)

    if test_imports():
        print("-" * 40)
        print("All dependencies installed successfully!")
        sys.exit(0)
    else:
        print("-" * 40)
        print("Some dependencies are missing. Please run: pip install -r requirements.txt")
        sys.exit(1)