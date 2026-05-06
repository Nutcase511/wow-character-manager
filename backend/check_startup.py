# 简单的启动验证脚本
import sys
import os

def check_environment():
    """检查环境配置"""
    print("Checking environment...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"[FAIL] Python version must be 3.8+, got {python_version.major}.{python_version.minor}")
        return False

    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[OK] Virtual environment is active")
    else:
        print("[WARN] Virtual environment is not active")

    # 检查.env文件
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"[OK] {env_file} file exists")
    else:
        print(f"[WARN] {env_file} file not found. Please copy .env.example to .env and configure it.")

    return True

def check_imports():
    """检查必要的导入"""
    print("\nChecking required packages...")

    packages = [
        'fastapi',
        'uvicorn',
        'motor',
        'pydantic',
        'httpx',
        'dotenv'
    ]

    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[FAIL] {package} - not installed")
            all_ok = False

    return all_ok

def check_project_structure():
    """检查项目结构"""
    print("\nChecking project structure...")

    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/schemas',
        'app/services'
    ]

    required_files = [
        'main.py',
        'requirements.txt'
    ]

    all_ok = True

    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"[OK] Directory {dir_path} exists")
        else:
            print(f"[FAIL] Directory {dir_path} not found")
            all_ok = False

    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"[OK] File {file_path} exists")
        else:
            print(f"[FAIL] File {file_path} not found")
            all_ok = False

    return all_ok

def main():
    print("=" * 50)
    print("WoW Character Manager - Startup Check")
    print("=" * 50)

    env_ok = check_environment()
    imports_ok = check_imports()
    structure_ok = check_project_structure()

    print("\n" + "=" * 50)
    if env_ok and imports_ok and structure_ok:
        print("All checks passed! Ready to start.")
        print("=" * 50)
        print("\nTo start the server, run:")
        print("python -m uvicorn main:app --reload")
        return 0
    else:
        print("Some checks failed. Please fix the issues above.")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())