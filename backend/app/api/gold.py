from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.schemas import (
    CharacterGoldResponse,
    GoldTransactionResponse,
    GoldSnapshotResponse,
    GoldSummaryResponse
)
from app.core.database import db

router = APIRouter()


def _row_to_gold(row):
    return {
        "id": row["id"],
        "character_id": row["character_id"],
        "character_name": row["character_name"],
        "realm": row["realm"],
        "current_gold": row["current_gold"],
        "last_updated": row["last_updated"]
    }


def _row_to_transaction(row):
    return {
        "id": row["id"],
        "character_id": row["character_id"],
        "source": row["source"],
        "source_title": row["source_title"],
        "time_mode": row["time_mode"],
        "amount_in": row["amount_in"],
        "amount_out": row["amount_out"],
        "recorded_at": row["recorded_at"]
    }


def _row_to_snapshot(row):
    return {
        "id": row["id"],
        "character_id": row["character_id"],
        "gold_amount": row["gold_amount"],
        "snapshot_date": row["snapshot_date"]
    }


@router.get("/all", response_model=List[CharacterGoldResponse])
async def get_all_gold():
    """获取所有角色的金币信息"""
    rows = await db.fetchall("SELECT cg.*, c.level FROM character_gold cg JOIN characters c ON cg.character_id = c.id ORDER BY c.level DESC")
    return [CharacterGoldResponse(**_row_to_gold(row)) for row in rows]


@router.get("/character/{character_id}", response_model=GoldSummaryResponse)
async def get_character_gold_summary(character_id: int, time_mode: str = "Total"):
    """获取指定角色的金币汇总信息"""
    # 获取角色当前金币
    gold_row = await db.fetchone(
        "SELECT * FROM character_gold WHERE character_id = ?", 
        (character_id,)
    )
    
    character_gold = None
    if gold_row:
        character_gold = CharacterGoldResponse(**_row_to_gold(gold_row))
    
    # 获取交易记录
    rows = await db.fetchall(
        "SELECT * FROM gold_transaction WHERE character_id = ? AND time_mode = ? ORDER BY source",
        (character_id, time_mode)
    )
    transactions = [GoldTransactionResponse(**_row_to_transaction(row)) for row in rows]
    
    # 计算总计
    total_in = sum(t.amount_in for t in transactions)
    total_out = sum(t.amount_out for t in transactions)
    net = total_in - total_out
    
    return GoldSummaryResponse(
        character_gold=character_gold,
        total_in=total_in,
        total_out=total_out,
        net=net,
        transactions=transactions
    )


@router.get("/character/{character_id}/transactions", response_model=List[GoldTransactionResponse])
async def get_character_transactions(character_id: int, time_mode: Optional[str] = None):
    """获取指定角色的交易记录"""
    if time_mode:
        rows = await db.fetchall(
            "SELECT * FROM gold_transaction WHERE character_id = ? AND time_mode = ? ORDER BY source",
            (character_id, time_mode)
        )
    else:
        rows = await db.fetchall(
            "SELECT * FROM gold_transaction WHERE character_id = ? ORDER BY time_mode, source",
            (character_id,)
        )
    return [GoldTransactionResponse(**_row_to_transaction(row)) for row in rows]


@router.get("/character/{character_id}/snapshots", response_model=List[GoldSnapshotResponse])
async def get_character_snapshots(character_id: int, limit: int = 30):
    """获取指定角色的金币快照历史"""
    rows = await db.fetchall(
        "SELECT * FROM gold_snapshot WHERE character_id = ? ORDER BY snapshot_date DESC LIMIT ?",
        (character_id, limit)
    )
    return [GoldSnapshotResponse(**_row_to_snapshot(row)) for row in rows]


@router.post("/character/{character_id}/update")
async def update_character_gold(character_id: int, gold_copper: int):
    """更新角色当前金币"""
    # 获取角色信息
    char_row = await db.fetchone(
        "SELECT name, realm FROM characters WHERE id = ?",
        (character_id,)
    )
    
    if not char_row:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # 检查是否存在记录
    existing = await db.fetchone(
        "SELECT id FROM character_gold WHERE character_id = ?",
        (character_id,)
    )
    
    if existing:
        await db.execute("""
            UPDATE character_gold
            SET current_gold = ?, last_updated = CURRENT_TIMESTAMP
            WHERE character_id = ?
        """, (gold_copper, character_id))
    else:
        await db.execute("""
            INSERT INTO character_gold (character_id, character_name, realm, current_gold)
            VALUES (?, ?, ?, ?)
        """, (character_id, char_row["name"], char_row["realm"], gold_copper))
    
    # 添加快照
    await db.execute("""
        INSERT INTO gold_snapshot (character_id, gold_amount)
        VALUES (?, ?)
    """, (character_id, gold_copper))
    
    return {"success": True, "message": "Gold updated successfully"}


@router.delete("/character/{character_id}")
async def delete_character_gold(character_id: int):
    """删除角色的金币数据"""
    await db.execute("DELETE FROM gold_transaction WHERE character_id = ?", (character_id,))
    await db.execute("DELETE FROM gold_snapshot WHERE character_id = ?", (character_id,))
    await db.execute("DELETE FROM character_gold WHERE character_id = ?", (character_id,))
    
    return {"success": True, "message": "Gold data deleted successfully"}
