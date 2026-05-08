import asyncio
import sys
import os
from fastapi import APIRouter, HTTPException
from typing import List, Optional

# 将 backend 目录加入路径以便导入 import_accountant
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.schemas.schemas import (
    CharacterGoldResponse,
    GoldTransactionResponse,
    GoldSnapshotResponse,
    GoldSummaryResponse
)
from app.core.database import db

# 导入 Accountant's Lua 解析/导入函数（同步的，丢线程池跑）
from import_accountant import find_accountant_files, parse_lua_file, import_accountant_data, ADDON_DIR, DATA_DB

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


@router.post("/refresh")
async def refresh_gold():
    """从 Accountant's Lua 文件重新导入最新金币数据"""
    import traceback
    try:
        accountant_files = find_accountant_files(ADDON_DIR)
        if not accountant_files:
            raise HTTPException(status_code=404, detail="未找到Accountant数据文件，请确认游戏已保存数据")

        total_chars = 0
        total_trans = 0
        errors = []

        for file_path in accountant_files:
            try:
                data = parse_lua_file(file_path)
                if data:
                    chars, trans = await asyncio.to_thread(import_accountant_data, data, DATA_DB)
                    total_chars += chars
                    total_trans += trans
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")

        if errors and total_chars == 0:
            raise HTTPException(status_code=500, detail=f"导入失败: {'; '.join(errors)}")

        return {
            "success": True,
            "message": f"同步完成！角色: {total_chars}, 交易: {total_trans}",
            "characters": total_chars,
            "transactions": total_trans,
            "errors": errors if errors else None
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


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
