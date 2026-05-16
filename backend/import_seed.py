"""
种子数据导入脚本
将 JSON 种子数据导入 SQLite 数据库
清空目标表后重新插入，保证数据一致性
"""
import sqlite3
import json
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "wow_character_manager.db")
SEED_DIR = os.path.join(BACKEND_DIR, "seed_data")

IMPORT_TABLES = [
    "dungeons",
    "bosses",
    "boss_loot",
    "items",
    "bis_lists",
    "talent_trees",
    "talent_nodes",
    "talent_builds",
]


def import_table(conn, table_name):
    filepath = os.path.join(SEED_DIR, f"{table_name}.json")
    if not os.path.exists(filepath):
        print(f"  -- {table_name}.json 不存在，跳过")
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print(f"  -- {table_name}.json 为空，跳过")
        return 0

    columns = list(data[0].keys())
    placeholders = ", ".join(["?" for _ in columns])
    col_names = ", ".join(columns)

    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

    for row in data:
        values = [row.get(col) for col in columns]
        cursor.execute(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", values)

    conn.commit()

    print(f"  ✅ {table_name}.json  ({len(data)} 条)")
    return len(data)


def main():
    if not os.path.exists(SEED_DIR):
        print(f"** 种子数据目录不存在: {SEED_DIR}")
        print("请先运行 export_seed.py 导出数据")
        return

    print(f"** 种子数据目录: {SEED_DIR}")
    print(f"** 目标数据库: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    total = 0
    for table in IMPORT_TABLES:
        count = import_table(conn, table)
        total += count

    conn.close()

    print(f"\n** 导入完成！共 {total} 条数据，{len(IMPORT_TABLES)} 个表")
    print("提示：导入后建议重启后端服务")


if __name__ == "__main__":
    main()