"""
系统配置API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import glob as glob_module
import re

from app.core.config import settings as app_settings

router = APIRouter(tags=["settings"])


class SettingsRequest(BaseModel):
    accountantPath: Optional[str] = ""
    tdinspectPath: Optional[str] = ""
    atlaslootPath: Optional[str] = ""
    titanbisPath: Optional[str] = ""


class SettingsResponse(BaseModel):
    accountantPath: str = ""
    tdinspectPath: str = ""
    atlaslootPath: str = ""
    # 数据库中的原始配置
    dbAccountantPath: Optional[str] = None
    dbTdinspectPath: Optional[str] = None
    dbAtlaslootPath: Optional[str] = None
    # 默认配置
    defaultAccountantPath: str = ""
    defaultTdinspectPath: str = ""
    defaultAtlaslootPath: str = ""


class StatsResponse(BaseModel):
    characters: int = 0
    dungeons: int = 0
    bosses: int = 0
    items: int = 0


class DirectoryItem(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int = 0


def get_db():
    conn = sqlite3.connect(app_settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
async def get_settings(includeSource: bool = False):
    """获取系统配置（合并数据库配置和默认配置）"""
    conn = get_db()
    cursor = conn.cursor()

    # 检查是否存在settings表
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='settings'
    """)
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

    cursor.execute("SELECT key, value FROM settings")
    db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()

    # 合并后的配置（数据库配置优先）
    merged = {
        'accountantPath': db_settings.get('accountant_path') or app_settings.DEFAULT_ACCOUNTANT_PATH,
        'tdinspectPath': db_settings.get('tdinspect_path') or app_settings.DEFAULT_TDINSPECT_PATH,
        'atlaslootPath': db_settings.get('atlasloot_path') or app_settings.DEFAULT_ATLASLOOT_PATH,
        'titanbisPath': db_settings.get('titanbis_path') or app_settings.DEFAULT_TITANBIS_PATH
    }

    if includeSource:
        merged['dbAccountantPath'] = db_settings.get('accountant_path')
        merged['dbTdinspectPath'] = db_settings.get('tdinspect_path')
        merged['dbAtlaslootPath'] = db_settings.get('atlasloot_path')
        merged['dbTitanbisPath'] = db_settings.get('titanbis_path')
        merged['defaultAccountantPath'] = app_settings.DEFAULT_ACCOUNTANT_PATH
        merged['defaultTdinspectPath'] = app_settings.DEFAULT_TDINSPECT_PATH
        merged['defaultAtlaslootPath'] = app_settings.DEFAULT_ATLASLOOT_PATH
        merged['defaultAcebisPath'] = app_settings.DEFAULT_ACEBIS_PATH

    return merged


@router.post("")
async def save_settings(settings: SettingsRequest):
    """保存系统配置"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    settings_data = [
        ('accountant_path', settings.accountantPath),
        ('tdinspect_path', settings.tdinspectPath),
        ('atlasloot_path', settings.atlaslootPath),
        ('titanbis_path', settings.titanbisPath)
    ]

    for key, value in settings_data:
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))

    conn.commit()
    conn.close()

    return {"message": "设置保存成功"}


@router.get("/test")
async def test_connections():
    """测试数据源连接"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT key, value FROM settings WHERE key IN (?, ?, ?, ?)",
                   ('accountant_path', 'tdinspect_path', 'atlasloot_path', 'titanbis_path'))
    db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()

    results = {
        "accountant": {"exists": False, "path": db_settings.get('accountant_path', '')},
        "tdinspect": {"exists": False, "path": db_settings.get('tdinspect_path', '')},
        "atlasloot": {"exists": False, "path": db_settings.get('atlasloot_path', '')},
        "titanbis": {"exists": False, "path": db_settings.get('titanbis_path', '')}
    }

    if results["accountant"]["path"] and os.path.exists(results["accountant"]["path"]):
        results["accountant"]["exists"] = True

    if results["tdinspect"]["path"] and os.path.exists(results["tdinspect"]["path"]):
        results["tdinspect"]["exists"] = True

    if results["atlasloot"]["path"] and os.path.exists(results["atlasloot"]["path"]):
        results["atlasloot"]["exists"] = True

    if results["titanbis"]["path"] and os.path.exists(results["titanbis"]["path"]):
        results["titanbis"]["exists"] = True

    all_exist = all(r["exists"] for r in results.values() if r["path"])

    return {
        "success": all_exist,
        "results": results
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取数据统计"""
    conn = get_db()
    cursor = conn.cursor()

    stats = StatsResponse()

    cursor.execute("SELECT COUNT(*) FROM characters")
    stats.characters = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dungeons")
    stats.dungeons = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bosses")
    stats.bosses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items")
    items_count = cursor.fetchone()[0]
    if items_count == 0:
        try:
            cursor.execute("SELECT COUNT(*) FROM loot_items")
            items_count = cursor.fetchone()[0]
        except:
            pass
    stats.items = items_count

    conn.close()
    return stats


@router.get("/browse")
async def browse_directory(path: str = "", file_type: str = ""):
    """浏览目录结构，用于文件/文件夹选择"""
    if not path:
        # 返回常用根目录
        drives = []
        for letter in "CDEFGH":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append({
                    "name": drive,
                    "path": drive,
                    "is_dir": True
                })
        return {"current_path": "", "items": drives, "parent": ""}

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"路径不存在: {path}")

    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"不是目录: {path}")

    items = []
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)
            size = 0 if is_dir else os.path.getsize(full_path)

            # 根据 file_type 过滤
            if file_type == "file" and is_dir:
                # 显示目录但不过滤
                pass
            elif file_type == "dir" and not is_dir:
                continue
            elif file_type == "lua" and not is_dir and not entry.lower().endswith('.lua'):
                continue

            items.append({
                "name": entry,
                "path": full_path,
                "is_dir": is_dir,
                "size": size
            })
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"无权限访问: {path}")

    # 目录排前，字母排序
    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

    parent = os.path.dirname(path) if path and len(path) > 3 else ""

    return {
        "current_path": path,
        "items": items,
        "parent": parent
    }


@router.get("/auto-detect")
async def auto_detect_wow_paths():
    """自动检测 WoW 安装目录和插件 SavedVariables 路径"""
    results = {
        "accountantPath": "",
        "tdinspectPath": "",
        "atlaslootPath": "",
        "titanbisPath": "",
        "wow_dir": "",
        "detected": False
    }

    # 常见 WoW 安装目录模式
    wow_patterns = [
        r"C:\WOW\World of Warcraft*",
        r"C:\Program Files*\World of Warcraft*",
        r"C:\Games\World of Warcraft*",
        r"D:\WOW\World of Warcraft*",
        r"D:\World of Warcraft*",
        r"D:\Games\World of Warcraft*",
        r"E:\WOW\World of Warcraft*",
        r"E:\World of Warcraft*",
    ]

    wow_dirs = []
    for pattern in wow_patterns:
        wow_dirs.extend(glob_module.glob(pattern))

    # 也检查已配置路径中的 WoW 目录
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("SELECT key, value FROM settings WHERE key IN (?, ?, ?)",
                   ('accountant_path', 'tdinspect_path', 'atlasloot_path'))
    db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()

    for val in db_settings.values():
        if val and "World of Warcraft" in val:
            # 从已有路径反推 WoW 根目录
            idx = val.find("World of Warcraft")
            candidate = val[:val.find("\\", idx + len("World of Warcraft"))] if "\\" in val[idx + len("World of Warcraft"):] else val[:idx + len("World of Warcraft")]
            # 需要找到 _classic_titan_ 的父目录
            for suffix in ["_classic_titan_"]:
                if suffix in val:
                    parent_end = val.find(suffix)
                    wow_dirs.append(val[:parent_end].rstrip("\\"))
                    break

    wow_dirs = list(set(wow_dirs))

    for wow_dir in wow_dirs:
        # 查找 WTF/Account 目录
        wtf_path = os.path.join(wow_dir, "_classic_titan_", "WTF", "Account")
        if not os.path.exists(wtf_path):
            continue

        # 查找 AddOns 目录
        addons_path = os.path.join(wow_dir, "_classic_titan_", "Interface", "AddOns")

        # 遍历 Account 下的账号目录
        for account_dir in os.listdir(wtf_path):
            account_path = os.path.join(wtf_path, account_dir)
            if not os.path.isdir(account_path):
                continue
            if account_dir in ("SavedVariables",):
                continue

            sv_path = os.path.join(account_path, "SavedVariables")
            if not os.path.exists(sv_path):
                continue

            # 检测 Accountant
            accountant_file = os.path.join(sv_path, "Accountant_Classic.lua")
            if os.path.exists(accountant_file) and not results["accountantPath"]:
                results["accountantPath"] = accountant_file

            # 检测 tdInspect
            tdinspect_file = os.path.join(sv_path, "tdInspect.lua")
            if os.path.exists(tdinspect_file) and not results["tdinspectPath"]:
                results["tdinspectPath"] = tdinspect_file

            # 检测 AtlasLoot
            if os.path.exists(addons_path):
                for addon_dir in os.listdir(addons_path):
                    if addon_dir.lower().startswith("atlasloot") and "my" in addon_dir.lower():
                        atlasloot_dir = os.path.join(addons_path, addon_dir)
                        if os.path.isdir(atlasloot_dir) and not results["atlaslootPath"]:
                            results["atlaslootPath"] = atlasloot_dir

                    # 检测 TitanBistooltip
                    if addon_dir.lower() == "titanbistooltip":
                        titanbis_dir = os.path.join(addons_path, addon_dir)
                        if os.path.isdir(titanbis_dir) and not results["titanbisPath"]:
                            results["titanbisPath"] = titanbis_dir

        if results["accountantPath"] or results["tdinspectPath"] or results["atlaslootPath"]:
            results["detected"] = True
            results["wow_dir"] = wow_dir
            break

    return results


@router.get("/auto-detect/{detect_type}")
async def auto_detect_single_path(detect_type: str):
    """自动检测单个插件路径"""
    valid_types = {"accountant", "tdinspect", "atlasloot", "titanbis"}
    if detect_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"无效的检测类型: {detect_type}")

    all_results = await auto_detect_wow_paths()

    key_map = {
        "accountant": "accountantPath",
        "tdinspect": "tdinspectPath",
        "atlasloot": "atlaslootPath",
        "titanbis": "titanbisPath"
    }

    path_key = key_map[detect_type]
    return {
        "type": detect_type,
        "path": all_results.get(path_key, ""),
        "wow_dir": all_results.get("wow_dir", ""),
        "detected": bool(all_results.get(path_key))
    }


@router.post("/import-bis")
async def import_bis_data():
    """从 TitanBistooltip 插件重新导入重铸泰坦 BiS 数据"""
    import re

    conn_sync = get_db()
    cursor = conn_sync.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'titanbis_path'")
    row = cursor.fetchone()
    conn_sync.close()

    titanbis_path = row['value'] if row else ""
    data_dir = os.path.join(titanbis_path, "data") if titanbis_path else ""

    if not data_dir or not os.path.exists(data_dir):
        raise HTTPException(status_code=400, detail="TitanBistooltip 插件路径未配置或data目录不存在")

    # 类名映射
    class_name_map = {
        "Death knight": "dk", "Druid": "druid", "Hunter": "hunter",
        "Mage": "mage", "Paladin": "paladin", "Priest": "priest",
        "Rogue": "rogue", "Shaman": "shaman", "Warlock": "warlock",
        "Warrior": "warrior",
    }

    line_header_re = re.compile(
        r'TitanBistooltip_Titan_bislists\["([^"]+)"\]\["([^"]+)"\]\["(\w+)"\]\[(\d+)\]'
    )
    slot_name_re = re.compile(r'\["slot_name"\]\s*=\s*"([^"]+)"')
    rank_item_re = re.compile(r'\[(\d+)\]\s*=\s*(-?\d+)')

    entries = []
    for class_dir_name in os.listdir(data_dir):
        class_path = os.path.join(data_dir, class_dir_name)
        if not os.path.isdir(class_path):
            continue
        for lua_file in os.listdir(class_path):
            if not lua_file.endswith('.lua'):
                continue
            filepath = os.path.join(class_path, lua_file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            for line in content.split('\n'):
                line = line.strip()
                if not line or '= {}' in line or 'or {}' in line:
                    continue
                hdr = line_header_re.search(line)
                if not hdr:
                    continue
                file_class = hdr.group(1)
                file_spec = hdr.group(2)
                phase = hdr.group(3)
                slot_m = slot_name_re.search(line)
                if not slot_m:
                    continue
                slot_name = slot_m.group(1)
                tail = line[slot_m.end():]
                for rm in rank_item_re.finditer(tail):
                    rank_num = int(rm.group(1))
                    item_id = int(rm.group(2))
                    if rank_num < 1 or rank_num > 6 or item_id <= 0:
                        continue
                    entries.append({
                        "class_name": class_name_map.get(file_class, file_class.lower()),
                        "spec_name": file_spec,
                        "rank": rank_num,
                        "item_id": item_id,
                        "phase": phase,
                        "slot": slot_name,
                    })

    if not entries:
        raise HTTPException(status_code=404, detail="未找到 BiS 数据")

    # 确保 bis_lists 表存在
    await db.execute("""
        CREATE TABLE IF NOT EXISTS bis_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            spec_name TEXT NOT NULL,
            phase TEXT NOT NULL,
            slot TEXT NOT NULL,
            rank INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            item_name TEXT,
            quality TEXT,
            item_level INTEGER DEFAULT 0,
            icon_url TEXT,
            source TEXT,
            dungeon_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(class_name, spec_name, phase, slot, rank, item_id)
        )
    """)

    # 清空旧数据
    await db.execute("DELETE FROM bis_lists")

    # 预加载关联数据
    item_rows = await db.fetchall("SELECT item_id, name, quality, item_level, icon_url FROM items")
    items_map = {r["item_id"]: r for r in item_rows}

    loot_rows = await db.fetchall("""
        SELECT bl.item_id, b.name as boss_name, b.dungeon_name
        FROM boss_loot bl JOIN bosses b ON bl.boss_id = b.boss_id
    """)
    loot_map = {}
    for r in loot_rows:
        if r["item_id"] not in loot_map:
            loot_map[r["item_id"]] = {"boss_name": r["boss_name"], "dungeon_name": r["dungeon_name"]}

    imported = 0
    for entry in entries:
        item_id = entry["item_id"]
        item_info = items_map.get(item_id)
        loot_info = loot_map.get(item_id)

        await db.execute("""
            INSERT OR IGNORE INTO bis_lists
            (class_name, spec_name, phase, slot, rank, item_id,
             item_name, quality, item_level, icon_url, source, dungeon_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry["class_name"], entry["spec_name"], entry["phase"],
            entry["slot"], entry["rank"], entry["item_id"],
            item_info["name"] if item_info else None,
            item_info["quality"] if item_info else None,
            item_info["item_level"] if item_info else 0,
            item_info["icon_url"] if item_info else None,
            loot_info["boss_name"] if loot_info else None,
            loot_info["dungeon_name"] if loot_info else None,
        ))
        imported += 1

    return {"success": True, "message": f"导入完成: {imported} 条 BiS 数据", "count": imported}


@router.delete("/clear-all")
async def clear_all_data():
    """清空所有数据（危险操作）"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        tables = ['characters', 'bosses', 'dungeons', 'items', 'loot_items',
                  'character_items', 'gold_records', 'talents',
                  'character_equipment', 'character_item_sets', 'boss_loot',
                  'gold_transaction', 'gold_snapshot', 'item_needs',
                  'talent_builds']

        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                pass

        conn.commit()
        conn.close()

        return {"message": "所有数据已清空"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")
