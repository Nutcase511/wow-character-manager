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
from import_accountant import find_accountant_files, parse_lua_file, import_accountant_data, ADDON_DIR as ACC_ADDON_DIR, DATA_DB
from import_tdinspect import parse_tdinspect_lua, name_to_key, CLASS_ID_MAP_WOTLK

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
        accountant_files = find_accountant_files(ACC_ADDON_DIR)
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


@router.get("/stats/monthly")
async def get_monthly_gold_stats(period: str = "month"):
    """获取按日/月/年统计的金币数据（用于图表）"""
    # 获取交易记录并按不同粒度分组
    if period == "year":
        # 按年查看时，按月份统计
        rows = await db.fetchall("""
            SELECT strftime('%Y-%m', recorded_at) as period,
                   SUM(amount_in) as total_in,
                   SUM(amount_out) as total_out
            FROM gold_transaction
            GROUP BY strftime('%Y-%m', recorded_at)
            ORDER BY period
        """)
    elif period == "month":
        # 按月查看时，按日期统计
        rows = await db.fetchall("""
            SELECT strftime('%Y-%m-%d', recorded_at) as period,
                   SUM(amount_in) as total_in,
                   SUM(amount_out) as total_out
            FROM gold_transaction
            GROUP BY strftime('%Y-%m-%d', recorded_at)
            ORDER BY period
        """)
    else:
        # 默认按日统计（周视图）
        rows = await db.fetchall("""
            SELECT strftime('%Y-%m-%d', recorded_at) as period,
                   SUM(amount_in) as total_in,
                   SUM(amount_out) as total_out
            FROM gold_transaction
            GROUP BY strftime('%Y-%m-%d', recorded_at)
            ORDER BY period
        """)
    
    result = []
    for row in rows:
        result.append({
            "period": row["period"],
            "total_in": row["total_in"] or 0,
            "total_out": row["total_out"] or 0,
            "net": (row["total_in"] or 0) - (row["total_out"] or 0)
        })
    
    return result


@router.get("/stats/characters")
async def get_character_gold_stats():
    """获取各角色金币统计数据（用于柱状图对比）"""
    rows = await db.fetchall("""
        SELECT cg.character_id, cg.character_name, cg.realm, cg.current_gold, c.wow_class
        FROM character_gold cg
        LEFT JOIN characters c ON cg.character_id = c.id
        ORDER BY cg.current_gold DESC
    """)
    
    result = []
    for row in rows:
        result.append({
            "character_id": row["character_id"],
            "character_name": row["character_name"],
            "realm": row["realm"],
            "current_gold": row["current_gold"] or 0,
            "wow_class": row["wow_class"] or "unknown"
        })
    
    return result


@router.get("/stats/timeline")
async def get_gold_timeline(character_id: int = None):
    """获取金币时间线数据"""
    if character_id:
        # 获取单个角色的快照
        rows = await db.fetchall("""
            SELECT snapshot_date, gold_amount
            FROM gold_snapshot
            WHERE character_id = ?
            ORDER BY snapshot_date
        """, (character_id,))
    else:
        # 获取所有角色的最近快照
        rows = await db.fetchall("""
            SELECT cg.character_name, gs.snapshot_date, gs.gold_amount
            FROM gold_snapshot gs
            JOIN character_gold cg ON gs.character_id = cg.character_id
            WHERE (gs.character_id, gs.snapshot_date) IN (
                SELECT character_id, MAX(snapshot_date) 
                FROM gold_snapshot 
                GROUP BY character_id
            )
            ORDER BY gs.gold_amount DESC
        """)
    
    result = []
    for row in rows:
        result.append(dict(row))
    
    return result


@router.post("/snapshot/daily")
async def create_daily_snapshot():
    """创建每日金币快照（为所有角色记录当前金币）"""
    # 获取所有角色当前金币
    gold_rows = await db.fetchall("SELECT * FROM character_gold")
    
    if not gold_rows:
        return {"success": False, "message": "没有找到角色金币数据"}
    
    # 获取今天的日期
    today = await db.fetchone("SELECT DATE('now') as today")
    today_str = today["today"]
    
    # 检查今天是否已经创建过快照
    existing = await db.fetchone("""
        SELECT COUNT(*) as count 
        FROM gold_snapshot 
        WHERE DATE(snapshot_date) = ?
        LIMIT 1
    """, (today_str,))
    
    if existing["count"] > 0:
        return {"success": False, "message": "今日快照已存在", "count": 0}
    
    # 创建快照记录
    count = 0
    for row in gold_rows:
        await db.execute("""
            INSERT INTO gold_snapshot (character_id, gold_amount)
            VALUES (?, ?)
        """, (row["character_id"], row["current_gold"]))
        count += 1
    
    return {"success": True, "message": f"每日快照创建成功", "count": count}


@router.get("/stats/daily")
async def get_daily_stats(character_id: int = None):
    """获取每日金币统计数据（用于趋势图表）"""
    if character_id:
        rows = await db.fetchall("""
            SELECT DATE(snapshot_date) as date, 
                   AVG(gold_amount) as avg_gold,
                   MAX(gold_amount) as max_gold,
                   MIN(gold_amount) as min_gold
            FROM gold_snapshot
            WHERE character_id = ?
            GROUP BY DATE(snapshot_date)
            ORDER BY date
        """, (character_id,))
    else:
        # 获取所有角色每日的总金币
        rows = await db.fetchall("""
            SELECT DATE(gs.snapshot_date) as date,
                   SUM(gs.gold_amount) as total_gold
            FROM gold_snapshot gs
            GROUP BY DATE(gs.snapshot_date)
            ORDER BY date
        """)
    
    result = []
    for row in rows:
        result.append(dict(row))
    
    return result
