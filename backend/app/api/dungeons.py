from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.schemas import DungeonCreate, DungeonResponse
from app.core.database import db
from app.services.blizzard_api import blizzard_api
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/", response_model=DungeonResponse)
async def create_dungeon(dungeon: DungeonCreate):
    """创建副本"""
    dungeon_data = dungeon.dict()
    dungeon_data["created_at"] = datetime.utcnow()

    result = await db.get_database()["dungeons"].insert_one(dungeon_data)
    created_dungeon = await db.get_database()["dungeons"].find_one({"_id": result.inserted_id})

    return DungeonResponse(**created_dungeon)


@router.get("/", response_model=List[DungeonResponse])
async def get_dungeons():
    """获取所有副本"""
    dungeons = await db.get_database()["dungeons"].find().to_list(length=100)
    return [DungeonResponse(**dungeon) for dungeon in dungeons]


@router.get("/{dungeon_id}", response_model=DungeonResponse)
async def get_dungeon(dungeon_id: str):
    """获取指定副本"""
    if not ObjectId.is_valid(dungeon_id):
        raise HTTPException(status_code=400, detail="Invalid dungeon ID")

    dungeon = await db.get_database()["dungeons"].find_one({"_id": ObjectId(dungeon_id)})
    if not dungeon:
        raise HTTPException(status_code=404, detail="Dungeon not found")

    return DungeonResponse(**dungeon)


@router.post("/sync/{journal_instance_id}")
async def sync_dungeon_from_blizzard(journal_instance_id: int):
    """从暴雪API同步副本数据"""
    dungeon_data = await blizzard_api.get_journal_instance(journal_instance_id)
    if not dungeon_data:
        raise HTTPException(status_code=404, detail="Failed to fetch dungeon data from Blizzard API")

    # 检查是否已存在
    existing = await db.get_database()["dungeons"].find_one({"dungeon_id": journal_instance_id})
    if existing:
        # 更新现有记录
        await db.get_database()["dungeons"].update_one(
            {"dungeon_id": journal_instance_id},
            {"$set": {
                "name": dungeon_data["name"],
                "description": dungeon_data.get("description"),
                "map_name": dungeon_data.get("map"),
                "minimum_level": dungeon_data.get("minimum_level", 70),
                "modes": dungeon_data.get("modes", []),
                "icon_url": dungeon_data.get("icon"),
                "updated_at": datetime.utcnow()
            }}
        )
        updated_dungeon = await db.get_database()["dungeons"].find_one({"dungeon_id": journal_instance_id})
        return DungeonResponse(**updated_dungeon)
    else:
        # 创建新记录
        new_dungeon = {
            "dungeon_id": dungeon_data["id"],
            "name": dungeon_data["name"],
            "description": dungeon_data.get("description"),
            "map_name": dungeon_data.get("map"),
            "minimum_level": dungeon_data.get("minimum_level", 70),
            "modes": dungeon_data.get("modes", []),
            "icon_url": dungeon_data.get("icon"),
            "created_at": datetime.utcnow()
        }
        result = await db.get_database()["dungeons"].insert_one(new_dungeon)
        created_dungeon = await db.get_database()["dungeons"].find_one({"_id": result.inserted_id})
        return DungeonResponse(**created_dungeon)


@router.delete("/{dungeon_id}")
async def delete_dungeon(dungeon_id: str):
    """删除副本"""
    if not ObjectId.is_valid(dungeon_id):
        raise HTTPException(status_code=400, detail="Invalid dungeon ID")

    result = await db.get_database()["dungeons"].delete_one({"_id": ObjectId(dungeon_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dungeon not found")

    return {"message": "Dungeon deleted successfully"}