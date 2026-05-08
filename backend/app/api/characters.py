from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.schemas import CharacterCreate, CharacterResponse
from app.core.database import db
from app.core.config import settings
from datetime import datetime
import asyncio
import os
import sys
import sqlite3

router = APIRouter()

# tdInspect 目录（与 backend 同级的 backend 目录）
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from import_tdinspect import parse_tdinspect_lua, name_to_key, CLASS_ID_MAP_WOTLK, TDINSPECT_FILE


def _row_to_character(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "realm": row["realm"],
        "wow_class": row["wow_class"],
        "spec": row["spec"],
        "level": row["level"],
        "faction": row["faction"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.post("/refresh-levels", operation_id="refresh_character_levels")
async def refresh_character_levels():
    """从 tdInspect 插件数据同步角色等级和职业信息"""
    import traceback
    if not os.path.exists(TDINSPECT_FILE):
        raise HTTPException(status_code=404, detail="未找到tdInspect数据文件，请确认游戏已安装tdInspect插件")

    try:
        def _sync():
            characters = parse_tdinspect_lua(TDINSPECT_FILE)
            db_path = settings.SQLITE_DB_PATH
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, wow_class, level FROM characters")
            db_chars = {row["name"]: dict(row) for row in cursor.fetchall()}
            now = datetime.utcnow().isoformat()
            updated = 0
            skipped = 0
            for c in characters:
                char_name = name_to_key(c["name"])
                matched = db_chars.get(char_name)
                if not matched:
                    continue
                cls_id = c["class"]
                char_class = CLASS_ID_MAP_WOTLK.get(cls_id, None)
                if not char_class:
                    skipped += 1
                    continue
                char_level = c["level"] or 0
                updates = []
                if matched["wow_class"] != char_class:
                    updates.append(f"职业 {matched['wow_class']}→{char_class}")
                if matched["level"] != char_level and char_level > 0:
                    updates.append(f"等级 {matched['level']}→{char_level}")
                if updates:
                    cursor.execute(
                        "UPDATE characters SET wow_class=?, level=?, updated_at=? WHERE id=?",
                        (char_class, char_level, now, matched["id"])
                    )
                    updated += 1
                else:
                    skipped += 1
            conn.commit()
            conn.close()
            return updated, skipped

        updated, skipped = await asyncio.to_thread(_sync)
        return {
            "success": True,
            "message": f"同步完成！更新 {updated} 条，跳过 {skipped} 条",
            "updated": updated,
            "skipped": skipped
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    """创建新角色"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """INSERT INTO characters (name, realm, wow_class, spec, level, faction, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (character.name, character.realm, character.wow_class.value, character.spec,
         character.level, character.faction, now, now)
    )
    row = await db.fetchone("SELECT * FROM characters WHERE id = ?", (cursor.lastrowid,))
    return CharacterResponse(**_row_to_character(row))


@router.get("/", response_model=List[CharacterResponse])
async def get_characters():
    """获取所有角色"""
    rows = await db.fetchall("SELECT * FROM characters ORDER BY id DESC")
    return [CharacterResponse(**_row_to_character(r)) for r in rows]


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int):
    """获取指定角色"""
    row = await db.fetchone("SELECT * FROM characters WHERE id = ?", (character_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterResponse(**_row_to_character(row))


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: int, character: CharacterCreate):
    """更新角色信息"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """UPDATE characters SET name=?, realm=?, wow_class=?, spec=?, level=?, faction=?, updated_at=?
           WHERE id=?""",
        (character.name, character.realm, character.wow_class.value, character.spec,
         character.level, character.faction, now, character_id)
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    row = await db.fetchone("SELECT * FROM characters WHERE id = ?", (character_id,))
    return CharacterResponse(**_row_to_character(row))


@router.delete("/{character_id}")
async def delete_character(character_id: int):
    """删除角色"""
    cursor = await db.execute("DELETE FROM characters WHERE id = ?", (character_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted successfully"}
