"""
后端服务健康检查和故障诊断
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


async def check_mongodb():
    """检查MongoDB连接"""
    print("=" * 50)
    print("1. Check MongoDB Connection")
    print("=" * 50)

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        # 尝试连接
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("[OK] MongoDB connection successful")

        # 检查数据库
        db = client["wow_character_manager"]
        collections = await db.list_collection_names()
        print(f"[OK] Database connection successful")
        print(f"   Collections: {collections}")

        await client.close()
        return True

    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return False


async def check_config():
    """检查配置文件"""
    print("\n" + "=" * 50)
    print("2. 检查配置文件")
    print("=" * 50)

    env_file = ".env"

    if not os.path.exists(env_file):
        print(f"❌ 配置文件不存在: {env_file}")
        return False

    print(f"✅ 配置文件存在: {env_file}")

    # 读取配置文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键配置
    checks = {
        'MONGODB_URL': 'mongodb://localhost:27017',
        'BLIZZARD_CLIENT_ID': 'your_client_id',  # 检查是否为默认值
        'BLIZZARD_CLIENT_SECRET': 'your_client_secret',
        'BLIZZARD_REGION': 'cn'
    }

    all_good = True
    for key, expected_default in checks.items():
        if key in content:
            if 'your_client_id' in content and key in ['BLIZZARD_CLIENT_ID', 'BLIZZARD_CLIENT_SECRET']:
                print(f"⚠️  {key}: 使用默认值，需要配置真实凭证")
            else:
                print(f"✅ {key}: 已配置")
        else:
            print(f"❌ {key}: 未配置")
            all_good = False

    return all_good


async def check_fastapi():
    """检查FastAPI应用"""
    print("\n" + "=" * 50)
    print("3. 检查FastAPI应用")
    print("=" * 50)

    try:
        from main import app
        print("✅ FastAPI应用加载成功")
        print(f"   应用名称: {app.title}")
        print(f"   版本: {app.version}")
        return True
    except Exception as e:
        print(f"❌ FastAPI应用加载失败: {e}")
        return False


async def test_character_creation():
    """测试角色创建功能"""
    print("\n" + "=" * 50)
    print("4. 测试角色创建功能")
    print("=" * 50)

    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from datetime import datetime

        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["wow_character_manager"]

        # 创建测试角色
        test_character = {
            "name": "TestCharacter",
            "realm": "时光1",
            "wow_class": "warrior",
            "spec": "武器",
            "level": 80,
            "faction": "alliance",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        print(f"尝试创建测试角色: {test_character['name']}")

        result = await db["characters"].insert_one(test_character)

        if result.inserted_id:
            print(f"✅ 角色创建成功，ID: {result.inserted_id}")

            # 清理测试数据
            await db["characters"].delete_one({"_id": result.inserted_id})
            print(f"✅ 测试数据已清理")

            await client.close()
            return True
        else:
            print("❌ 角色创建失败")
            await client.close()
            return False

    except Exception as e:
        print(f"❌ 角色创建测试失败: {e}")
        return False


async def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 50)
    print("5. 检查依赖包")
    print("=" * 50)

    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('motor', 'Motor'),
        ('pydantic', 'Pydantic'),
        ('httpx', 'HTTPX')
    ]

    all_installed = True
    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {display_name}: 已安装")
        except ImportError:
            print(f"❌ {display_name}: 未安装")
            all_installed = False

    return all_installed


async def diagnose_500_error():
    """诊断500错误可能的原因"""
    print("\n" + "=" * 50)
    print("6. 500错误诊断")
    print("=" * 50)

    issues = []

    # 检查常见问题
    try:
        # 检查配置
        env_content = open('.env').read()
        if 'your_client_id' in env_content:
            issues.append("暴雪API凭证未配置，API调用可能失败")

        # 检查MongoDB
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        try:
            await client.admin.command('ping')
        except:
            issues.append("MongoDB连接失败")

        # 检查数据验证
        from app.schemas.schemas import CharacterCreate
        try:
            test_data = {
                "name": "Test",
                "realm": "时光1",
                "wow_class": "warrior",
                "spec": "武器",
                "level": 80,
                "faction": "alliance"
            }
            CharacterCreate(**test_data)
        except Exception as e:
            issues.append(f"数据验证失败: {e}")

    except Exception as e:
        issues.append(f"诊断过程出错: {e}")

    if issues:
        print("发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print("✅ 未发现明显的500错误原因")
        return True


async def main():
    """主诊断函数"""
    print("WoW Character Manager - Diagnostic Tool")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # 执行各项检查
    results.append(("MongoDB Connection", await check_mongodb()))
    results.append(("Configuration File", await check_config()))
    results.append(("FastAPI Application", await check_fastapi()))
    results.append(("Character Creation Test", await test_character_creation()))
    results.append(("Dependencies", await check_dependencies()))
    results.append(("500 Error Diagnosis", await diagnose_500_error()))

    # 输出总结
    print("\n" + "=" * 50)
    print("Diagnostic Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{check_name}: {status}")

    print(f"\nOverall result: {passed}/{total} checks passed")

    # 提供建议
    print("\nSuggestions:")
    if passed < total:
        print("1. Please fix the failed issues above")
        print("2. Ensure MongoDB is running")
        print("3. Check .env file configuration")
        print("4. Ensure all dependencies are installed")
    else:
        print("System is healthy and ready to use")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
    except Exception as e:
        print(f"\n\n诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()