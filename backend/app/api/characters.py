from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.schemas import CharacterCreate, CharacterResponse
from app.core.database import db
from app.models.models import Character
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/", response_model=CharacterResponse)
async def create_character(character: CharacterCreate):
    """创建新角色"""
    character_data = character.dict()
    character_data["created_at"] = datetime.utcnow()
    character_data["updated_at"] = datetime.utcnow()

    result = await db.get_database()["characters"].insert_one(character_data)
    created_character = await db.get_database()["characters"].find_one({"_id": result.inserted_id})

    return CharacterResponse(**created_character)


@router.get("/", response_model=List[CharacterResponse])
async def get_characters():
    """获取所有角色"""
    characters = await db.get_database()["characters"].find().to_list(length=100)
    return [CharacterResponse(**char) for char in characters]


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """获取指定角色"""
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID")

    character = await db.get_database()["characters"].find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return CharacterResponse(**character)


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: str, character: CharacterCreate):
    """更新角色信息"""
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID")

    character_data = character.dict()
    character_data["updated_at"] = datetime.utcnow()

    result = await db.get_database()["characters"].update_one(
        {"_id": ObjectId(character_id)},
        {"$set": character_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")

    updated_character = await db.get_database()["characters"].find_one({"_id": ObjectId(character_id)})
    return CharacterResponse(**updated_character)


@router.delete("/{character_id}")
async def delete_character(character_id: str):
    """删除角色"""
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID")

    result = await db.get_database()["characters"].delete_one({"_id": ObjectId(character_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")

    return {"message": "Character deleted successfully"}