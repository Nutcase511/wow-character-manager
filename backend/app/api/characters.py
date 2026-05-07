from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.schemas import CharacterCreate, CharacterResponse
from app.core.database import db
from datetime import datetime

router = APIRouter()


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
