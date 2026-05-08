import aiosqlite
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = settings.SQLITE_DB_PATH
        self._connection: aiosqlite.Connection = None

    async def connect(self):
        """连接数据库"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        print(f"Connected to SQLite: {self.db_path}")

    async def ensure_connection(self):
        """确保数据库连接可用，不可用时自动重连"""
        if self._connection is None:
            logger.info("Database connection is None, reconnecting...")
            await self.connect()
            return
        try:
            # 尝试执行简单查询来验证连接是否还活着
            await self._connection.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Database connection lost ({e}), reconnecting...")
            try:
                await self._connection.close()
            except Exception:
                pass
            self._connection = None
            await self.connect()

    async def close(self):
        """关闭连接"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            print("Closed SQLite connection")

    async def init_tables(self):
        """创建所有表"""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                realm TEXT NOT NULL,
                wow_class TEXT NOT NULL,
                spec TEXT,
                level INTEGER DEFAULT 80,
                faction TEXT DEFAULT 'horde',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                quality TEXT NOT NULL,
                item_level INTEGER DEFAULT 0,
                slot TEXT,
                stats TEXT DEFAULT '{}',
                icon_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS dungeons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dungeon_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                map_name TEXT,
                minimum_level INTEGER DEFAULT 70,
                modes TEXT DEFAULT '[]',
                expansion TEXT DEFAULT 'wotlk',
                category TEXT DEFAULT 'dungeon',
                icon_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bosses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                boss_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                dungeon_id INTEGER,
                dungeon_name TEXT,
                category TEXT,
                icon_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS item_needs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                boss_id INTEGER,
                boss_name TEXT,
                dungeon_name TEXT,
                priority INTEGER DEFAULT 1,
                obtained INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            );

            CREATE TABLE IF NOT EXISTS boss_loot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                boss_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                item_name TEXT,
                difficulty TEXT DEFAULT '',
                FOREIGN KEY (boss_id) REFERENCES bosses(boss_id)
            );

            CREATE TABLE IF NOT EXISTS character_gold (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                character_name TEXT NOT NULL,
                realm TEXT NOT NULL,
                current_gold INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id),
                UNIQUE(character_id)
            );

            CREATE TABLE IF NOT EXISTS gold_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                source_title TEXT NOT NULL,
                time_mode TEXT NOT NULL,
                amount_in INTEGER DEFAULT 0,
                amount_out INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            );

            CREATE TABLE IF NOT EXISTS gold_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                gold_amount INTEGER NOT NULL,
                snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id)
            );
        """)
        await self._connection.commit()
        print("Database tables initialized")

    def get_connection(self) -> aiosqlite.Connection:
        return self._connection

    async def fetchone(self, query: str, params=()):
        """执行查询并返回一行"""
        await self.ensure_connection()
        cursor = await self._connection.execute(query, params)
        return await cursor.fetchone()

    async def fetchall(self, query: str, params=()):
        """执行查询并返回所有行"""
        await self.ensure_connection()
        cursor = await self._connection.execute(query, params)
        return await cursor.fetchall()

    async def execute(self, query: str, params=()):
        """执行写操作并返回cursor"""
        await self.ensure_connection()
        cursor = await self._connection.execute(query, params)
        await self._connection.commit()
        return cursor


db = Database()
