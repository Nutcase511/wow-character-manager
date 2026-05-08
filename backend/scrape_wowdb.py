import sqlite3
import requests
import json
import time
import random

def fetch_item_name_wowdb(item_id):
    """从WoWDB获取装备的中文名称"""
    # WoWDB提供API接口
    url = f"https://www.wowdb.com/api/item/{item_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.