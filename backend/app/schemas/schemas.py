from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class WoWClass(str, Enum):
    WARRIOR = "warrior"
    PALADIN = "paladin"
    HUNTER = "hunter"
    ROGUE = "rogue"
    PRIEST = "priest"
    DEATH_KNIGHT = "death_knight"
    SHAMAN = "shaman"
    MAGE = "mage"
    WARLOCK = "warlock"
    MONK = "monk"
    DRUID = "druid"
    DEMON_HUNTER = "demon_hunter"
    EVOKER = "evoker"


class ItemQuality(str, Enum):
    POOR = "poor"
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class CharacterCreate(BaseModel):
    name: str = Field(..., description="角色名称")
    realm: str = Field(..., description="服务器名称")
    wow_class: WoWClass = Field(..., description="职业")
    spec: Optional[str] = Field(None, description="专精")
    level: int = Field(80, description="等级")
    faction: str = Field("horde", description="阵营")


class CharacterResponse(BaseModel):
    id: int
    name: str
    realm: str
    wow_class: str
    spec: Optional[str]
    level: int
    faction: str
    race: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    equips_data: Optional[str] = None
    talents_data: Optional[str] = None
    active_talent_group: Optional[int] = None


class ItemCreate(BaseModel):
    item_id: int
    name: str
    quality: ItemQuality
    item_level: int
    slot: Optional[str] = None
    stats: Dict[str, int] = {}
    icon_url: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    item_id: int
    name: str
    quality: str
    item_level: int
    slot: Optional[str]
    stats: Dict[str, int]
    icon_url: Optional[str]
    created_at: Optional[str] = None


class DungeonCreate(BaseModel):
    dungeon_id: int
    name: str
    description: Optional[str] = None
    map_name: Optional[str] = None
    minimum_level: int = 70
    modes: List[str] = []
    expansion: str = "wotlk"
    category: str = "dungeon"
    icon_url: Optional[str] = None


class DungeonResponse(BaseModel):
    id: int
    dungeon_id: int
    name: str
    description: Optional[str]
    map_name: Optional[str]
    minimum_level: int
    modes: List[str]
    expansion: str = "wotlk"
    category: str = "dungeon"
    icon_url: Optional[str]
    created_at: Optional[str] = None


class BossCreate(BaseModel):
    boss_id: int
    name: str
    description: Optional[str] = None
    dungeon_id: int
    dungeon_name: str
    category: Optional[str] = None
    icon_url: Optional[str] = None


class BossResponse(BaseModel):
    id: int
    boss_id: int
    name: str
    description: Optional[str]
    dungeon_id: int
    dungeon_name: str
    category: Optional[str]
    icon_url: Optional[str]
    created_at: Optional[str] = None


class ItemNeedCreate(BaseModel):
    character_id: str
    item_id: int
    item_name: str
    boss_id: Optional[int] = None
    boss_name: Optional[str] = None
    dungeon_name: Optional[str] = None
    priority: int = Field(1, description="优先级 1-5")
    obtained: bool = False
    notes: Optional[str] = None


class ItemNeedResponse(BaseModel):
    id: int
    character_id: str
    item_id: int
    item_name: str
    boss_id: Optional[int]
    boss_name: Optional[str]
    dungeon_name: Optional[str]
    priority: int
    obtained: bool
    notes: Optional[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProgressCreate(BaseModel):
    character_id: str
    dungeon_id: int
    dungeon_name: str
    difficulty: str
    bosses_killed: List[int] = []
    last_updated: Optional[datetime] = None


class ProgressResponse(BaseModel):
    id: int
    character_id: str
    dungeon_id: int
    dungeon_name: str
    difficulty: str
    bosses_killed: List[int]
    last_updated: Optional[datetime]
    created_at: Optional[str] = None


class RealmResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: str
    locale: str
    timezone: str
    is_tournament: bool
    region: str


class CharacterGoldResponse(BaseModel):
    id: int
    character_id: int
    character_name: str
    realm: str
    current_gold: int
    last_updated: Optional[str] = None


class GoldTransactionResponse(BaseModel):
    id: int
    character_id: int
    source: str
    source_title: str
    time_mode: str
    amount_in: int
    amount_out: int
    recorded_at: Optional[str] = None


class GoldSnapshotResponse(BaseModel):
    id: int
    character_id: int
    gold_amount: int
    snapshot_date: Optional[str] = None


class GoldSummaryResponse(BaseModel):
    character_gold: Optional[CharacterGoldResponse] = None
    total_in: int
    total_out: int
    net: int
    transactions: List[GoldTransactionResponse] = []
