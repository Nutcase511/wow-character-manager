"""
将提取的魔兽世界数据导入到MongoDB
"""
import json
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Any


class WoWDataImporter:
    """魔兽世界数据导入器"""

    def __init__(self, mongodb_url: str = "mongodb://localhost:27017", db_name: str = "wow_character_manager"):
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.client = None
        self.database = None

    async def connect(self):
        """连接数据库"""
        self.client = AsyncIOMotorClient(self.mongodb_url)
        self.database = self.client[self.db_name]
        print(f"连接到MongoDB: {self.db_name}")

    async def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            print("关闭数据库连接")

    async def import_instances(self, instances_file: str):
        """导入副本数据"""
        if not os.path.exists(instances_file):
            print(f"副本数据文件不存在: {instances_file}")
            return

        print(f"开始导入副本数据: {instances_file}")

        with open(instances_file, 'r', encoding='utf-8') as f:
            instances = json.load(f)

        # 转换数据格式
        formatted_instances = []
        for instance in instances:
            formatted_instance = {
                "dungeon_id": instance['id'],
                "name": instance['name'],
                "description": instance.get('description', ''),
                "map_name": "",  # 需要从Map.dbc获取
                "minimum_level": 70,  # 时光服默认70级
                "modes": ["normal", "heroic"],  # 时光服难度
                "icon_url": None,
                "created_at": None  # 会在插入时设置
            }
            formatted_instances.append(formatted_instance)

        # 导入到数据库
        if formatted_instances:
            result = await self.database["dungeons"].insert_many(formatted_instances)
            print(f"成功导入 {len(result.inserted_ids)} 个副本")
        else:
            print("没有副本数据可导入")

    async def import_bosses(self, bosses_file: str, instances_data: List[Dict]):
        """导入Boss数据"""
        if not os.path.exists(bosses_file):
            print(f"Boss数据文件不存在: {bosses_file}")
            return

        print(f"开始导入Boss数据: {bosses_file}")

        with open(bosses_file, 'r', encoding='utf-8') as f:
            bosses = json.load(f)

        # 创建副本ID到名称的映射
        instance_map = {inst['dungeon_id']: inst['name'] for inst in instances_data}

        # 转换数据格式
        formatted_bosses = []
        for boss in bosses:
            instance_id = boss.get('instance_id')
            instance_name = instance_map.get(instance_id, "未知副本")

            formatted_boss = {
                "boss_id": boss['id'],
                "name": boss['name'],
                "description": boss.get('description', ''),
                "dungeon_id": instance_id,
                "dungeon_name": instance_name,
                "category": "副本Boss",
                "icon_url": None,
                "created_at": None
            }
            formatted_bosses.append(formatted_boss)

        # 导入到数据库
        if formatted_bosses:
            result = await self.database["bosses"].insert_many(formatted_bosses)
            print(f"成功导入 {len(result.inserted_ids)} 个Boss")
        else:
            print("没有Boss数据可导入")

    async def import_items(self, items_file: str, limit: int = 1000):
        """导入装备数据"""
        if not os.path.exists(items_file):
            print(f"装备数据文件不存在: {items_file}")
            return

        print(f"开始导入装备数据: {items_file} (限制: {limit}个)")

        with open(items_file, 'r', encoding='utf-8') as f:
            items = json.load(f)

        # 装备类别名称映射
        item_classes = {
            0: "消耗品",
            1: "容器",
            2: "武器",
            3: "宝石",
            4: "护甲",
            5: "试剂",
            6: "投射物",
            7: "贸易商品",
            8: "通用",
            9: "配方",
            10: "货币",
            11: "任务物品",
            12: "钥匙",
            13: "永久性",
            15: "杂项"
        }

        # 装备品质映射
        quality_map = {
            0: "poor",
            1: "common",
            2: "uncommon",
            3: "rare",
            4: "epic",
            5: "legendary",
            6: "artifact",
            7: "heirloom"
        }

        # 装备部位映射
        slot_map = {
            0: None,
            1: "头部",
            2: "颈部",
            3: "肩部",
            4: "衬衫",
            5: "胸部",
            6: "腰部",
            7: "腿部",
            8: "脚",
            9: "手腕",
            10: "手套",
            11: "手指",
            12: "饰品",
            13: "单手",
            14: "盾牌",
            15: "远程",
            16: "背部",
            17: "双手",
            18: "袋",
            19: "图腾",
            20: "弹药",
            21: "投掷",
            22: "Ranged",
            23: "Quiver",
            24: "Relic"
        }

        # 只导入装备类物品（护甲和武器）
        equipment_items = [item for item in items if item.get('item_class') in [2, 4]]

        # 限制导入数量
        equipment_items = equipment_items[:limit]

        formatted_items = []
        for item in equipment_items:
            item_class_id = item.get('item_class', 0)
            quality_id = item.get('quality', 1)
            slot_id = item.get('inventory_type', 0)

            formatted_item = {
                "item_id": item['id'],
                "name": item['name'],
                "quality": quality_map.get(quality_id, 'common'),
                "item_level": item.get('item_level', 1),
                "slot": slot_map.get(slot_id),
                "stats": {},  # 需要从Item.dbc获取详细属性
                "icon_url": None,
                "created_at": None
            }
            formatted_items.append(formatted_item)

        # 导入到数据库
        if formatted_items:
            result = await self.database["items"].insert_many(formatted_items)
            print(f"成功导入 {len(result.inserted_ids)} 个装备")
        else:
            print("没有装备数据可导入")

    async def import_all(self, data_dir: str = "./wow_data", item_limit: int = 1000):
        """导入所有数据"""
        print("开始导入所有魔兽世界数据...")
        print(f"数据目录: {data_dir}")

        await self.connect()

        try:
            # 导入副本
            instances_file = os.path.join(data_dir, "instances.json")
            if os.path.exists(instances_file):
                with open(instances_file, 'r', encoding='utf-8') as f:
                    instances_data = json.load(f)

                # 清空现有数据
                await self.database["dungeons"].delete_many({})
                await self.import_instances(instances_file)
            else:
                print("副本数据文件不存在，跳过")
                instances_data = []

            # 导入Boss
            bosses_file = os.path.join(data_dir, "bosses.json")
            if os.path.exists(bosses_file):
                # 清空现有数据
                await self.database["bosses"].delete_many({})
                await self.import_bosses(bosses_file, instances_data)
            else:
                print("Boss数据文件不存在，跳过")

            # 导入装备
            items_file = os.path.join(data_dir, "items.json")
            if os.path.exists(items_file):
                # 清空现有数据
                await self.database["items"].delete_many({})
                await self.import_items(items_file, item_limit)
            else:
                print("装备数据文件不存在，跳过")

            print("\n所有数据导入完成！")

        finally:
            await self.close()


async def main():
    """主函数"""
    print("魔兽世界数据导入工具")
    print("=" * 50)

    # 配置
    MONGODB_URL = "mongodb://localhost:27017"
    DATABASE_NAME = "wow_character_manager"
    DATA_DIR = "./wow_data"
    ITEM_LIMIT = 500  # 装备导入数量限制，避免数据过大

    print(f"MongoDB: {MONGODB_URL}")
    print(f"数据库: {DATABASE_NAME}")
    print(f"数据目录: {DATA_DIR}")
    print(f"装备导入限制: {ITEM_LIMIT}")

    # 确认导入
    confirm = input(f"\n确认导入数据？这将清空现有数据 (y/n): ").strip().lower()
    if confirm != 'y':
        print("操作取消")
        return

    # 执行导入
    importer = WoWDataImporter(MONGODB_URL, DATABASE_NAME)
    await importer.import_all(DATA_DIR, ITEM_LIMIT)


if __name__ == "__main__":
    asyncio.run(main())