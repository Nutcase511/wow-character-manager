"""
魔兽世界DBC文件解析器
用于从本地魔兽世界客户端读取游戏数据
"""
import struct
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DBCHeader:
    """DBC文件头"""
    magic: str           # 文件魔数 "WDBC"
    record_count: int    # 记录数量
    field_count: int     # 字段数量
    record_size: int     # 记录大小
    string_block_size: int  # 字符串块大小


class DBCReader:
    """DBC文件读取器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.header = None
        self.records = []
        self.string_block = b''

    def read(self) -> bool:
        """读取DBC文件"""
        if not os.path.exists(self.file_path):
            print(f"文件不存在: {self.file_path}")
            return False

        try:
            with open(self.file_path, 'rb') as f:
                # 读取文件头
                header_data = f.read(20)  # DBC头固定20字节
                self.header = self._parse_header(header_data)

                if not self.header:
                    return False

                # 读取记录数据
                records_data = f.read(self.header.record_count * self.header.record_size)

                # 读取字符串块
                self.string_block = f.read(self.header.string_block_size)

                # 解析记录
                self.records = self._parse_records(records_data)

            return True

        except Exception as e:
            print(f"读取DBC文件失败: {e}")
            return False

    def _parse_header(self, data: bytes) -> Optional[DBCHeader]:
        """解析DBC文件头"""
        try:
            magic, record_count, field_count, record_size, string_block_size = struct.unpack('<4sIIII', data)

            if magic != b'WDBC':
                print(f"无效的DBC文件魔数: {magic}")
                return None

            return DBCHeader(
                magic=magic.decode('ascii'),
                record_count=record_count,
                field_count=field_count,
                record_size=record_size,
                string_block_size=string_block_size
            )
        except Exception as e:
            print(f"解析文件头失败: {e}")
            return None

    def _parse_records(self, data: bytes) -> List[Dict[str, Any]]:
        """解析记录数据"""
        records = []

        for i in range(self.header.record_count):
            start = i * self.header.record_size
            end = start + self.header.record_size
            record_data = data[start:end]

            record = self._parse_record(record_data)
            records.append(record)

        return records

    def _parse_record(self, data: bytes) -> Dict[str, Any]:
        """解析单条记录（基类方法，子类需要重写）"""
        return {'raw_data': data}

    def get_string(self, offset: int) -> str:
        """从字符串块中获取字符串"""
        if offset < 0 or offset >= len(self.string_block):
            return ""

        try:
            end = self.string_block.find(b'\x00', offset)
            if end == -1:
                return self.string_block[offset:].decode('utf-8', errors='ignore')
            return self.string_block[offset:end].decode('utf-8', errors='ignore')
        except:
            return ""


class JournalInstanceReader(DBCReader):
    """副本信息读取器"""

    def _parse_record(self, data: bytes) -> Dict[str, Any]:
        """解析副本记录"""
        # JournalInstance.dbc 字段结构
        # ID, Name_lang, Description_lang, MapID, AreaID, ...

        # 解析字段（简化版本，根据实际结构调整）
        record_id = struct.unpack('<I', data[0:4])[0]

        # 字符串偏移量（需要根据实际字段位置调整）
        name_offset = struct.unpack('<I', data[4:8])[0]
        description_offset = struct.unpack('<I', data[8:12])[0]

        return {
            'id': record_id,
            'name': self.get_string(name_offset),
            'description': self.get_string(description_offset)
        }


class JournalEncounterReader(DBCReader):
    """Boss信息读取器"""

    def _parse_record(self, data: bytes) -> Dict[str, Any]:
        """解析Boss记录"""
        # JournalEncounter.dbc 字段结构
        # ID, Name_lang, Description_lang, JournalInstanceID, ...

        record_id = struct.unpack('<I', data[0:4])[0]
        name_offset = struct.unpack('<I', data[4:8])[0]
        description_offset = struct.unpack('<I', data[8:12])[0]
        instance_id_offset = struct.unpack('<I', data[12:16])[0]
        instance_id = struct.unpack('<I', data[instance_id_offset:instance_id_offset+4])[0]

        return {
            'id': record_id,
            'name': self.get_string(name_offset),
            'description': self.get_string(description_offset),
            'instance_id': instance_id
        }


class ItemSparseReader(DBCReader):
    """装备详细信息读取器"""

    def _parse_record(self, data: bytes) -> Dict[str, Any]:
        """解析装备记录"""
        # ItemSparse.dbc 字段结构（简化版本）
        # ID, Name_lang, Description_lang, Quality, ItemLevel, ClassID, SubClassID, InventoryType, ...

        record_id = struct.unpack('<I', data[0:4])[0]
        name_offset = struct.unpack('<I', data[4:8])[0]
        description_offset = struct.unpack('<I', data[8:12])[0]

        quality = struct.unpack('<I', data[12:16])[0]
        item_level = struct.unpack('<I', data[16:20])[0]
        item_class = struct.unpack('<I', data[20:24])[0]
        item_subclass = struct.unpack('<I', data[24:28])[0]
        inventory_type = struct.unpack('<I', data[28:32])[0]

        return {
            'id': record_id,
            'name': self.get_string(name_offset),
            'description': self.get_string(description_offset),
            'quality': quality,
            'item_level': item_level,
            'item_class': item_class,
            'item_subclass': item_subclass,
            'inventory_type': inventory_type
        }


def find_wow_directory() -> Optional[str]:
    """查找魔兽世界安装目录"""
    common_paths = [
        "C:/Program Files (x86)/World of Warcraft/_classic_/",
        "C:/Games/World of Warcraft/_classic_/",
        "D:/World of Warcraft/_classic_/",
        "E:/World of Warcraft/_classic_/",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None


def extract_wow_data(wow_path: str, output_dir: str = "./wow_data"):
    """从魔兽世界客户端提取数据"""

    dbc_path = os.path.join(wow_path, "DBFilesClient")

    if not os.path.exists(dbc_path):
        print(f"DBC目录不存在: {dbc_path}")
        return False

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"开始提取数据...")
    print(f"魔兽世界路径: {wow_path}")
    print(f"DBC文件路径: {dbc_path}")

    # 提取副本信息
    print("\n提取副本信息...")
    instance_file = os.path.join(dbc_path, "JournalInstance.dbc")
    if os.path.exists(instance_file):
        reader = JournalInstanceReader(instance_file)
        if reader.read():
            print(f"成功读取 {len(reader.records)} 个副本")
            # 保存为JSON
            import json
            with open(os.path.join(output_dir, "instances.json"), 'w', encoding='utf-8') as f:
                json.dump(reader.records, f, ensure_ascii=False, indent=2)
        else:
            print("读取副本信息失败")
    else:
        print(f"副本文件不存在: {instance_file}")

    # 提取Boss信息
    print("\n提取Boss信息...")
    encounter_file = os.path.join(dbc_path, "JournalEncounter.dbc")
    if os.path.exists(encounter_file):
        reader = JournalEncounterReader(encounter_file)
        if reader.read():
            print(f"成功读取 {len(reader.records)} 个Boss")
            import json
            with open(os.path.join(output_dir, "bosses.json"), 'w', encoding='utf-8') as f:
                json.dump(reader.records, f, ensure_ascii=False, indent=2)
        else:
            print("读取Boss信息失败")
    else:
        print(f"Boss文件不存在: {encounter_file}")

    # 提取装备信息
    print("\n提取装备信息...")
    item_file = os.path.join(dbc_path, "ItemSparse.dbc")
    if os.path.exists(item_file):
        reader = ItemSparseReader(item_file)
        if reader.read():
            print(f"成功读取 {len(reader.records)} 个装备")
            import json
            with open(os.path.join(output_dir, "items.json"), 'w', encoding='utf-8') as f:
                json.dump(reader.records, f, ensure_ascii=False, indent=2)
        else:
            print("读取装备信息失败")
    else:
        print(f"装备文件不存在: {item_file}")

    print(f"\n数据提取完成！文件保存在: {output_dir}")
    return True


if __name__ == "__main__":
    print("魔兽世界数据提取工具")
    print("=" * 50)

    # 查找魔兽世界目录
    wow_dir = find_wow_directory()

    if not wow_dir:
        print("未找到魔兽世界安装目录")
        print("请手动输入魔兽世界路径:")
        wow_dir = input().strip()

        if not os.path.exists(wow_dir):
            print("路径不存在，程序退出")
            exit(1)
    else:
        print(f"找到魔兽世界目录: {wow_dir}")

    # 确认提取
    confirm = input(f"\n是否从此路径提取数据？(y/n): ").strip().lower()
    if confirm != 'y':
        print("操作取消")
        exit(0)

    # 提取数据
    success = extract_wow_data(wow_dir)

    if success:
        print("\n提取成功！现在可以使用这些数据了。")
    else:
        print("\n提取失败，请检查路径和文件权限。")