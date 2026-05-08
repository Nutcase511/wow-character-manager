import sqlite3

# 精确翻译字典
chinese_item_names = {
    # ===== 材料 =====
    "Badge of Justice": "公正徽章",
    "Frozen Orb": "冰冻宝珠",
    "Primordial Saronite": "原始萨隆邪铁",
    "Shadowfrost Shard": "影霜碎片",
    "Fragment of Val'anyr": "瓦兰奈尔碎片",
    "Emblem of Conquest": "征服纹章",
    "Emblem of Triumph": "凯旋纹章",
    "Emblem of Frost": "冰霜纹章",
    "Trophy of the Crusade": "十字军战利品",
    "Champion's Seal": "冠军的徽记",
    # ===== 套装部件 =====
    "Spaulders of the Lost Vanquisher": "失落胜利者肩甲",
    "Spaulders of the Lost Protector": "失落守护者肩甲",
    "Spaulders of the Lost Conqueror": "失落征服者肩甲",
    "Leggings of the Lost Vanquisher": "失落胜利者护腿",
    "Leggings of the Lost Protector": "失落守护者护腿",
    "Leggings of the Lost Conqueror": "失落征服者护腿",
    "Helm of the Lost Vanquisher": "失落胜利者头盔",
    "Helm of the Lost Protector": "失落守护者头盔",
    "Helm of the Lost Conqueror": "失落征服者头盔",
    "Spaulders of the Wayward Vanquisher": "迷途胜利者肩甲",
    "Spaulders of the Wayward Protector": "迷途守护者肩甲",
    "Spaulders of the Wayward Conqueror": "迷途征服者肩甲",
    "Leggings of the Wayward Vanquisher": "迷途胜利者护腿",
    "Leggings of the Wayward Protector": "迷途守护者护腿",
    "Leggings of the Wayward Conqueror": "迷途征服者护腿",
    "Helm of the Wayward Vanquisher": "迷途胜利者头盔",
    "Helm of the Wayward Protector": "迷途守护者头盔",
    "Helm of the Wayward Conqueror": "迷途征服者头盔",
    "Gloves of the Wayward Vanquisher": "迷途胜利者手套",
    "Gloves of the Wayward Protector": "迷途守护者手套",
    "Gloves of the Wayward Conqueror": "迷途征服者手套",
    "Chestguard of the Wayward Vanquisher": "迷途胜利者胸甲",
    "Chestguard of the Wayward Protector": "迷途守护者胸甲",
    "Chestguard of the Wayward Conqueror": "迷途征服者胸甲",
    "Vanquisher's Mark of Sanctification": "胜利者的神圣印记",
    "Protector's Mark of Sanctification": "守护者的神圣印记",
    "Conqueror's Mark of Sanctification": "征服者的神圣印记",
    # ===== 经典装备 =====
    "Abomination Knuckles": "憎恶指节",
    "Abomination Shoulderblades": "憎恶肩刃",
    "Abyssal Rune": "深渊符文",
    "Ace of Beasts": "野兽王牌",
    "Acid Inscribed Pauldrons": "酸蚀肩甲",
    "Aegis of the Coliseum": "角斗场庇护",
    "Aesir's Edge": "艾西尔之刃",
    "Agamaggan's Clutch": "阿迦玛甘之握",
    "Alabaster Idol": "雪花石膏神像",
    "Aldori Legacy Defender": "奥尔多遗产防御者",
    "Ahn'kahar Handwraps": "安卡哈护手",
    "Crawler-Emblem Belt": "爬行者徽章腰带",
    "Blade of Nadox": "纳多克斯之刃",
    "Elder Headpiece": "长者头饰",
    "Sprinting Shoulderpads": "疾行肩垫",
    "Brood Plague Helmet": "虫群瘟疫头盔",
    "Nerubian Shield Ring": "蛛魔护盾指环",
    "Staff of the Plague Beast": "瘟疫兽法杖",
    "Scourgeborne Plate": "天灾板甲",
    "Cryptstalker Armor": "墓穴追踪者护甲",
    "Darkruned Armor": "暗纹护甲",
    "Ebon Blade Plate": "黑锋板甲",
    "Plagueheart Raiment": "瘟疫之心法衣",
    "Frostfire Regalia": "霜火套装",
    # ===== 纳克萨玛斯 =====
    "Kilt of Sewn Flesh": "缝合血肉褶裙",
    "Slaughterhouse Sabatons": "屠宰场战靴",
    "Enchanted Wire Stitching": "附魔钢丝缝线",
    "Meathook's Slicer": "肉钩的切割器",
    "Belt of Unified Souls": "灵魂统束腰带",
    "Bile-Cured Gloves": "胆汁浸洗手套",
    "Spaulders of the Abomination": "憎恶肩甲",
    "Legplates of Steel Implants": "钢铁植入护腿",
    "Shoulderpads of the Walking Plague": "瘟疫行者肩垫",
    "Plagueheart Robe": "瘟疫之心长袍",
    "Gloves of the Plaguebringer": "瘟疫使者手套",
    "Plague-Core Belt": "瘟疫核心腰带",
    "Plague Leggings": "瘟疫护腿",
    "Cloak of the Necropolis": "大墓地斗篷",
    "Crown of the Frost Wyrm": "冰霜巨龙之冠",
    "Frost Wyrm Cloak": "冰霜巨龙斗篷",
    "Phylactery of Kel'Thuzad": "克尔苏加德的护符匣",
    "Staff of the Frost Wyrm": "冰霜巨龙法杖",
    "Kel'Thuzad's Reach": "克尔苏加德之握",
    "Frostmourne's Hungry Blade": "霜之哀伤的饥渴之刃",
    "Chestguard of the Frozen Wastes": "冰封废土胸甲",
    "Helm of Domination": "统御头盔",
    "Boots of the Frozen Crypt": "冰封墓穴之靴",
    "Ring of the Archlich": "巫妖王之环",
    "Necklace of the Frozen Wastes": "冰封废土项链",
    "Gauntlets of the Warden": "典狱长护手",
    "Trousers of Eternity": "永恒护腿",
    # ===== 奥杜尔 =====
    "Val'anyr, Hammer of Ancient Kings": "瓦兰奈尔，远古王者之锤",
    "Mimiron's Head": "米米尔隆的头部",
    "Hand of Gul'dan": "古尔丹之手",
    "Titansteel Destroyer": "泰坦精钢毁灭者",
    "Fury of the Aspects": "守护巨龙之怒",
    "The Beholder": "魔眼",
    # ===== 十字军试炼 =====
    "Deathbringer's Will": "死亡使者的意志",
    "Triumphant Legplates": "凯旋护腿",
    "Crusader's Edge": "十字军之刃",
    "Lightsworn Greatsword": "圣光使者巨剑",
    "Valkyr's Kiss": "瓦格里之吻",
    "Frostsilk Robe": "霜丝长袍",
    # ===== 冰冠堡垒 =====
    "Shadowmourne": "影之哀伤",
    "Frostmourne": "霜之哀伤",
    "Blade of the Fallen Prince": "陨落王子之刃",
    # ===== 旧世经典 =====
    "Staff of Rampant Growth": "疯狂生长法杖",
    "Malfurion's Signet Ring": "玛法里奥的徽记之戒",
    "Hammer of Bestial Fury": "野兽之怒锤",
    "Green Dragonskin Cloak": "绿龙鳞披风",
    "Flamewaker Legplates": "烈焰行者腿甲",
    "Dragonbone Wristguards": "龙骨护腕",
    "Ancient Corroded Leggings": "远古腐蚀护腿",
    "Acid Inscribed Greaves": "酸蚀护胫",
    # ===== 更多装备 =====
    "Black Ice": "黑冰",
    "Hailstorm": "冰雹",
    "The Decapitator": "斩首者",
    "The Eye of Observation": "观察之眼",
    "Zul'Drak Slicer": "祖达克切割者",
    "Saronite Razor": "萨隆邪铁剃刀",
    "Titansteel Bonebreaker": "泰坦精钢碎骨锤",
    "Froststeel Longsword": "霜钢长剑",
    "Shadow Edge": "暗影边缘",
    "Death's Verdict": "死亡裁决",
    "Comet's Trail": "彗星之尾",
    "Mirror of Truth": "真相之镜",
    "Solace of the Fallen": "陨落慰藉",
    "Spark of Hope": "希望火花",
    "Frost Lotus": "冰霜莲花",
    "Tears of the Vanquished": "战败者之泪",
    "Talisman of Resurgence": "复苏护符",
    "Ashbringer": "灰烬使者",
    "Atiesh, Greatstaff of the Guardian": "埃提耶什，守护者的传说之杖",
    "Thori'dal, the Stars' Fury": "索利达尔，群星之怒",
    "Warglaive of Azzinoth": "埃辛诺斯战刃",
    # ===== 宝石袋 =====
    "Yellow Sack of Gems": "黄色宝石袋",
    "Sack of Gems": "宝石袋",
    "Red Sack of Gems": "红色宝石袋",
    "Green Sack of Gems": "绿色宝石袋",
    "Gray Sack of Gems": "灰色宝石袋",
    "Blue Sack of Gems": "蓝色宝石袋",
    # ===== 冬季帽子 =====
    "Red Winter Hat": "红色冬帽",
    "Green Winter Hat": "绿色冬帽",
    # ===== 安其拉 =====
    "Imperial Qiraji Regalia": "其拉帝王徽记",
    "Imperial Qiraji Armaments": "其拉帝王武器",
    "Qiraji Spiked Hilt": "其拉尖刺剑柄",
    "Qiraji Ornate Hilt": "其拉华丽剑柄",
    "Qiraji Martial Drape": "其拉军用披风",
    "Qiraji Regal Drape": "其拉皇家披风",
    "Qiraji Magisterial Ring": "其拉执政官戒指",
    "Qiraji Ceremonial Ring": "其拉仪式戒指",
}

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 更新boss_loot表
updated_count = 0
for english, chinese in chinese_item_names.items():
    cursor.execute('UPDATE boss_loot SET item_name = ? WHERE item_name = ?', (chinese, english))
    updated_count += cursor.rowcount

conn.commit()
print(f'Updated {updated_count} loot entries')

# 更新items表
item_updates = 0
for english, chinese in chinese_item_names.items():
    cursor.execute('UPDATE items SET name = ? WHERE name = ?', (chinese, english))
    item_updates += cursor.rowcount

conn.commit()
print(f'Updated {item_updates} items')

conn.close()
