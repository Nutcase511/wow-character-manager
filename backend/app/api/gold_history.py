from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, Date

from app.db import get_db
from app.models import CharacterGoldHistory, CharacterGold

router = APIRouter(prefix="/api/gold/history", tags=["gold-history"])


@router.post("/snapshot")
async def create_daily_snapshot(db=Depends(get_db)):
    """创建每日金币快照"""
    today = date.today()
    
    # 获取所有角色当前金币
    gold_items = await db.execute(select(CharacterGold))
    gold_records = gold_items.scalars().all()
    
    # 检查今天是否已经创建过快照
    existing_check = await db.execute(
        select(CharacterGoldHistory).where(
            CharacterGoldHistory.date == today
        ).limit(1)
    )
    
    if existing_check.scalars().first():
        return {"message": "今日快照已存在", "count": 0}
    
    # 创建快照记录
    count = 0
    for gold in gold_records:
        history = CharacterGoldHistory(
            character_id=gold.character_id,
            character_name=gold.character_name,
            realm=gold.realm,
            gold_amount=gold.current_gold,
            date=today
        )
        db.add(history)
        count += 1
    
    await db.commit()
    return {"message": "快照创建成功", "count": count}


@router.get("/daily")
async def get_daily_history(
    character_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db=Depends(get_db)
):
    """获取每日金币历史记录"""
    query = select(CharacterGoldHistory)
    
    if character_id:
        query = query.where(CharacterGoldHistory.character_id == character_id)
    
    if start_date:
        query = query.where(CharacterGoldHistory.date >= start_date)
    
    if end_date:
        query = query.where(CharacterGoldHistory.date <= end_date)
    
    query = query.order_by(CharacterGoldHistory.date)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/monthly")
async def get_monthly_stats(
    character_id: Optional[str] = None,
    year: int = Query(default_factory=lambda: datetime.now().year),
    db=Depends(get_db)
):
    """获取月度金币统计"""
    # 计算每个月的收入和支出
    subq = select(
        CharacterGoldHistory.character_id,
        CharacterGoldHistory.character_name,
        func.strftime("%Y-%m", CharacterGoldHistory.date).label("month"),
        CharacterGoldHistory.gold_amount,
        CharacterGoldHistory.date
    ).subquery()
    
    query = select(
        subq.c.character_id,
        subq.c.character_name,
        subq.c.month,
        func.max(subq.c.gold_amount).label("max_gold"),
        func.min(subq.c.gold_amount).label("min_gold"),
        func.avg(subq.c.gold_amount).label("avg_gold")
    ).group_by(subq.c.character_id, subq.c.character_name, subq.c.month)
    
    if character_id:
        query = query.where(subq.c.character_id == character_id)
    
    result = await db.execute(query)
    return result.all()


@router.get("/trend")
async def get_gold_trend(
    character_id: Optional[str] = None,
    period: str = "month",  # month or year
    db=Depends(get_db)
):
    """获取金币趋势数据"""
    now = datetime.now()
    
    if period == "year":
        # 获取今年每月的数据
        start_date = date(now.year, 1, 1)
        end_date = date(now.year, 12, 31)
        date_format = "%Y-%m"
    else:
        # 获取本月每日的数据
        start_date = date(now.year, now.month, 1)
        end_date = date(now.year, now.month, 1)
        date_format = "%Y-%m-%d"
    
    query = select(
        CharacterGoldHistory.character_id,
        CharacterGoldHistory.character_name,
        func.strftime(date_format, CharacterGoldHistory.date).label("period"),
        func.avg(CharacterGoldHistory.gold_amount).label("avg_gold"),
        func.sum(CharacterGoldHistory.gold_amount).label("total_gold")
    ).where(
        CharacterGoldHistory.date >= start_date
    ).group_by(
        CharacterGoldHistory.character_id,
        CharacterGoldHistory.character_name,
        func.strftime(date_format, CharacterGoldHistory.date)
    ).order_by(
        func.strftime(date_format, CharacterGoldHistory.date)
    )
    
    if character_id:
        query = query.where(CharacterGoldHistory.character_id == character_id)
    
    result = await db.execute(query)
    return result.all()