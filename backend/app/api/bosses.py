from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.schemas import BossCreate, BossResponse
from app.core.database import db
from app.services.blizzard_api import blizzard_api
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/", response_model=BossResponse)
async def create_boss(boss: BossCreate):
    """创建Boss"""
    boss_data = boss.dict()
    boss_data["created_at"] = datetime.utcnow()

    result = await db.get_database()["bosses"].insert_one(boss_data)
    created_boss = await db.get_database()["bosses"].find_one({"_id": result.inserted_id})

    return BossResponse(**created_boss)


@router.get("/", response_model=List[BossResponse])
async def get_bosses(dungeon_id: int = None):
    """获取所有Boss"""
    query = {}
    if dungeon_id:
        query["dungeon_id"] = dungeon_id

    bosses = await db.get_database()["bosses"].find(query).to_list(length=100)
    return [BossResponse(**boss) for boss in bosses]


@router.get("/{boss_id}", response_model=BossResponse)
async def get_boss(boss_id: str):
    """获取指定Boss"""
    if not ObjectId.is_valid(boss_id):
        raise HTTPException(status_code=400, detail="Invalid boss ID")

    boss = await db.get_database()["bosses"].find_one({"_id": ObjectId(boss_id)})
    if not boss:
        raise HTTPException(status_code=404, detail="Boss not found")

    return BossResponse(**boss)


@router.post("/sync/{journal_encounter_id}")
async def sync_boss_from_blizzard(journal_encounter_id: int):
    """从暴雪API同步Boss数据"""
    boss_data = await blizzard_api.get_journal_encounter(journal_encounter_id)
    if not boss_data:
        raise HTTPException(status_code=404, detail="Failed to fetch boss data from Blizzard API")

    # 检查是否已存在
    existing = await db.get_database()["bosses"].find_one({"boss_id": journal_encounter_id})
    if existing:
        # 更新现有记录
        await db.get_database()["bosses"].update_one(
            {"boss_id": journal_encounter_id},
            {"$set": {
                "name": boss_data["name"],
                "description": boss_data.get("description"),
                "dungeon_name": boss_data.get("instance"),
                "category": boss_data.get("category"),
                "icon_url": boss_data.get("icon"),
                "updated_at": datetime.utcnow()
            }}
        )
        updated_boss = await db.get_database()["bosses"].find_one({"boss_id": journal_encounter_id})
        return BossResponse(**updated_boss)
    else:
        # 创建新记录
        new_boss = {
            "boss_id": boss_data["id"],
            "name": boss_data["name"],
            "description": boss_data.get("description"),
            "dungeon_id": boss_data.get("id"),  # 这可能需要从instance数据中获取
            "dungeon_name": boss_data.get("instance"),
            "category": boss_data.get("category"),
            "icon_url": boss_data.get("icon"),
            "created_at": datetime.utcnow()
        }
        result = await db.get_database()["bosses"].insert_one(new_boss)
        created_boss = await db.get_database()["bosses"].find_one({"_id": result.inserted_id})
        return BossResponse(**created_boss)


@router.get("/dungeon/{dungeon_id}/bosses", response_model=List[BossResponse])
async def get_bosses_by_dungeon(dungeon_id: int):
    """获取指定副本的所有Boss"""
    bosses = await db.get_database()["bosses"].find({"dungeon_id": dungeon_id}).to_list(length=50)
    return [BossResponse(**boss) for boss in bosses]


@router.delete("/{boss_id}")
async def delete_boss(boss_id: str):
    """删除Boss"""
    if not ObjectId.is_valid(boss_id):
        raise HTTPException(status_code=400, detail="Invalid boss ID")

    result = await db.get_database()["bosses"].delete_one({"_id": ObjectId(boss_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Boss not found")

    return {"message": "Boss deleted successfully"}