from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Character(MongoBaseModel):
    name: str
    realm: str
    wow_class: str
    spec: Optional[str]
    level: int = 70
    faction: str = "alliance"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Item(MongoBaseModel):
    item_id: int
    name: str
    quality: str
    item_level: int
    slot: Optional[str]
    stats: Dict[str, int] = {}
    icon_url: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Dungeon(MongoBaseModel):
    dungeon_id: int
    name: str
    description: Optional[str]
    map_name: Optional[str]
    minimum_level: int = 70
    modes: List[str] = []
    icon_url: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Boss(MongoBaseModel):
    boss_id: int
    name: str
    description: Optional[str]
    dungeon_id: int
    dungeon_name: str
    category: Optional[str]
    icon_url: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ItemNeed(MongoBaseModel):
    character_id: str
    item_id: int
    item_name: str
    boss_id: Optional[int]
    boss_name: Optional[str]
    dungeon_name: Optional[str]
    priority: int = 1
    obtained: bool = False
    notes: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Progress(MongoBaseModel):
    character_id: str
    dungeon_id: int
    dungeon_name: str
    difficulty: str
    bosses_killed: List[int] = []
    last_updated: Optional[datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)