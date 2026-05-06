"""
服务器API测试脚本
测试从暴雪API获取服务器列表的功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.blizzard_api import blizzard_api


async def test_realms_api():
    """测试服务器API功能"""

    print("=" * 60)
    print("测试暴雪API服务器获取功能")
    print("=" * 60)

    # 测试获取怀旧服服务器列表
    print("\n[1/3] 测试获取怀旧服服务器列表...")
    try:
        classic_realms = await blizzard_api.get_realms(classic=True)
        if classic_realms:
            print(f"✓ 成功获取 {len(classic_realms)} 个怀旧服服务器")
            print("前5个服务器:")
            for i, realm in enumerate(classic_realms[:5], 1):
                print(f"  {i}. {realm['name']} ({realm['slug']}) - {realm['category']}")
        else:
            print("✗ 未能获取怀旧服服务器列表")
    except Exception as e:
        print(f"✗ 获取怀旧服服务器失败: {e}")

    # 测试获取正式服服务器列表
    print("\n[2/3] 测试获取正式服服务器列表...")
    try:
        retail_realms = await blizzard_api.get_realms(classic=False)
        if retail_realms:
            print(f"✓ 成功获取 {len(retail_realms)} 个正式服服务器")
            print("前5个服务器:")
            for i, realm in enumerate(retail_realms[:5], 1):
                print(f"  {i}. {realm['name']} ({realm['slug']}) - {realm['category']}")
        else:
            print("✗ 未能获取正式服服务器列表")
    except Exception as e:
        print(f"✗ 获取正式服服务器失败: {e}")

    # 测试获取指定服务器信息
    print("\n[3/3] 测试获取指定服务器信息...")
    test_realm_slug = "stormrage"  # 测试用的服务器slug
    try:
        realm_info = await blizzard_api.get_realm(test_realm_slug, classic=False)
        if realm_info:
            print(f"✓ 成功获取服务器信息:")
            print(f"  名称: {realm_info['name']}")
            print(f"  Slug: {realm_info['slug']}")
            print(f"  分类: {realm_info['category']}")
            print(f"  时区: {realm_info['timezone']}")
            print(f"  区域: {realm_info['region']}")
        else:
            print(f"✗ 未能获取服务器 '{test_realm_slug}' 的信息")
    except Exception as e:
        print(f"✗ 获取服务器信息失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


async def test_realm_search():
    """测试服务器搜索功能"""
    print("\n" + "=" * 60)
    print("测试服务器搜索功能")
    print("=" * 60)

    try:
        # 获取服务器列表
        realms = await blizzard_api.get_realms(classic=True)

        if not realms:
            print("✗ 未能获取服务器列表，无法测试搜索功能")
            return

        # 测试搜索
        search_terms = ["艾泽拉斯", "世界", "服"]

        for term in search_terms:
            print(f"\n搜索 '{term}':")
            results = [r for r in realms if term in r['name'] or term in r['slug']]
            if results:
                print(f"  找到 {len(results)} 个结果:")
                for i, realm in enumerate(results[:3], 1):
                    print(f"    {i}. {realm['name']} ({realm['slug']})")
            else:
                print(f"  未找到匹配结果")

    except Exception as e:
        print(f"✗ 搜索测试失败: {e}")


async def test_realm_filtering():
    """测试服务器过滤功能"""
    print("\n" + "=" * 60)
    print("测试服务器过滤功能")
    print("=" * 60)

    try:
        realms = await blizzard_api.get_realms(classic=True)

        if not realms:
            print("✗ 未能获取服务器列表")
            return

        # 按分类统计
        categories = {}
        for realm in realms:
            category = realm.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        print("\n按分类统计:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} 个服务器")

        # 按时区统计
        timezones = {}
        for realm in realms:
            timezone = realm.get('timezone', 'unknown')
            timezones[timezone] = timezones.get(timezone, 0) + 1

        print("\n按时区统计:")
        for timezone, count in sorted(timezones.items())[:5]:  # 只显示前5个
            print(f"  {timezone}: {count} 个服务器")

    except Exception as e:
        print(f"✗ 过滤测试失败: {e}")


async def main():
    """主函数"""
    try:
        await test_realms_api()
        await test_realm_search()
        await test_realm_filtering()

        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)
        print("\n提示: 如果测试失败，请检查:")
        print("1. .env文件中的暴雪API凭证是否正确")
        print("2. 网络连接是否正常")
        print("3. 暴雪API服务是否可用")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())