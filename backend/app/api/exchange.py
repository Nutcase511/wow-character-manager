from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.core.database import db

router = APIRouter(prefix="/api/exchange", tags=["exchange"])


@router.get("/token/current")
async def get_current_token_price():
    """获取最新的时光徽章价格"""
    row = await db.fetchone(
        "SELECT * FROM token_prices ORDER BY recorded_at DESC LIMIT 1"
    )
    if not row:
        return {"price_gold": None, "recorded_at": None, "source": None}
    return {
        "id": row["id"],
        "price_gold": row["price_gold"],
        "source": row["source"],
        "notes": row["notes"],
        "recorded_at": row["recorded_at"]
    }


@router.get("/token/history")
async def get_token_price_history(limit: int = Query(30, ge=1, le=365)):
    """获取时光徽章价格历史"""
    rows = await db.fetchall(
        "SELECT * FROM token_prices ORDER BY recorded_at DESC LIMIT ?",
        (limit,)
    )
    return [
        {
            "id": r["id"],
            "price_gold": r["price_gold"],
            "source": r["source"],
            "notes": r["notes"],
            "recorded_at": r["recorded_at"]
        }
        for r in rows
    ]


@router.post("/token/record")
async def record_token_price(price_gold: int, notes: Optional[str] = None):
    """记录新的时光徽章价格"""
    if price_gold <= 0:
        raise HTTPException(status_code=400, detail="价格必须大于0")
    cursor = await db.execute(
        "INSERT INTO token_prices (price_gold, source, notes) VALUES (?, ?, ?)",
        (price_gold, "manual", notes)
    )
    return {"id": cursor.lastrowid, "price_gold": price_gold, "message": "记录成功"}


@router.get("/rate/current")
async def get_current_exchange_rate():
    """获取当前金币兑换汇率"""
    row = await db.fetchone(
        "SELECT * FROM exchange_rates ORDER BY recorded_at DESC LIMIT 1"
    )
    if not row:
        return {"gold_per_cny": None, "recorded_at": None}
    return {
        "id": row["id"],
        "gold_per_cny": row["gold_per_cny"],
        "source": row["source"],
        "notes": row["notes"],
        "recorded_at": row["recorded_at"]
    }


@router.get("/rate/history")
async def get_exchange_rate_history(limit: int = Query(30, ge=1, le=365)):
    """获取汇率历史"""
    rows = await db.fetchall(
        "SELECT * FROM exchange_rates ORDER BY recorded_at DESC LIMIT ?",
        (limit,)
    )
    return [
        {
            "id": r["id"],
            "gold_per_cny": r["gold_per_cny"],
            "source": r["source"],
            "notes": r["notes"],
            "recorded_at": r["recorded_at"]
        }
        for r in rows
    ]


@router.post("/rate/record")
async def record_exchange_rate(gold_per_cny: float, notes: Optional[str] = None):
    """记录新的金币兑换汇率"""
    if gold_per_cny <= 0:
        raise HTTPException(status_code=400, detail="汇率必须大于0")
    cursor = await db.execute(
        "INSERT INTO exchange_rates (gold_per_cny, source, notes) VALUES (?, ?, ?)",
        (gold_per_cny, "manual", notes)
    )
    return {"id": cursor.lastrowid, "gold_per_cny": gold_per_cny, "message": "记录成功"}


@router.get("/calculate")
async def calculate_exchange(
    gold: Optional[int] = Query(None, ge=0),
    cny: Optional[float] = Query(None, ge=0)
):
    """金币兑换计算器：输入金币或人民币，计算对应金额"""
    rate_row = await db.fetchone(
        "SELECT gold_per_cny FROM exchange_rates ORDER BY recorded_at DESC LIMIT 1"
    )
    token_row = await db.fetchone(
        "SELECT price_gold FROM token_prices ORDER BY recorded_at DESC LIMIT 1"
    )

    gold_per_cny = rate_row["gold_per_cny"] if rate_row else None
    token_price = token_row["price_gold"] if token_row else None

    if gold is not None and gold_per_cny:
        cny_result = round(gold / gold_per_cny, 2)
        tokens = round(gold / token_price, 2) if token_price else None
        return {
            "gold": gold,
            "cny": cny_result,
            "rate": gold_per_cny,
            "token_price": token_price,
            "token_count": tokens
        }
    elif cny is not None and gold_per_cny:
        gold_result = round(cny * gold_per_cny)
        tokens = round(gold_result / token_price, 2) if token_price else None
        return {
            "gold": gold_result,
            "cny": cny,
            "rate": gold_per_cny,
            "token_price": token_price,
            "token_count": tokens
        }
    else:
        return {
            "gold": None,
            "cny": None,
            "rate": gold_per_cny,
            "token_price": token_price,
            "message": "请提供 gold 或 cny 参数" if not gold_per_cny else "请提供 gold 或 cny 参数"
        }