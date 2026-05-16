"""
种子数据导出脚本
将参考/种子数据从 SQLite 导出为 JSON 文件，用于 git 版本控制
排除用户相关数据（角色、装备、金币等）
"""
import sqlite3
import json
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "wow_character_manager.db")
SEED_DIR = os.path.join(BACKEND_DIR, "seed_data")

EXPORT_TABLES = {
    "dungeons": "副本数据",
    "bosses": "首领数据",
    "boss_loot": "首领掉落",
    "items": "装备物品",
    "bis_lists": "各职业毕业装备(BiS)",
    "talent_trees": "天赋树",
    "talent_nodes": "天赋节点",
    "talent_builds": "天赋配点",
}


def export_table(conn, table_name, label):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    data = []
    for row in rows:
        item = {}
        for i, col in enumerate(columns):
            val = row[i]
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="replace")
            item[col] = val
        data.append(item)

    filepath = os.path.join(SEED_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK {table_name}.json  ({len(data)} 条) — {label}")
    return len(data)


def main():
    os.makedirs(SEED_DIR, exist_ok=True)

    print(f"** 种子数据导出目录: {SEED_DIR}")
    print(f"** 数据库: {DB_PATH}")
    print()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    total = 0
    for table, label in EXPORT_TABLES.items():
        count = export_table(conn, table, label)
        total += count

    conn.close()

    print(f"\n** 导出完成！共 {total} 条数据，{len(EXPORT_TABLES)} 个表")


if __name__ == "__main__":
    main()