local AceGUI = LibStub("AceGUI-3.0")

-- 传说装备名称列表
TitanBistooltip_legendary_names = {
    ["雷霆之怒，逐风者的祝福之剑"] = true,
    ["萨弗拉斯，炎魔拉格纳罗斯之手"] = true,
    ["埃提耶什，守护者的传说之杖"] = true,
    ["瓦兰奈尔，远古王者之锤"] = true,
    ["玛尔沃罗斯，污染者碎片"] = true,
    ["索利达尔，群星之怒"] = true,
    ["埃辛诺斯战刃"] = true,
    ["缚灵碎片护符"] = true,
    ["影之哀伤"] = true,
}

-- 消耗品数据
TitanBistooltip_consumables = {
    -- 法系消耗品
    caster = {
        slot_name = "consumables",
        [1] = 46376, -- 冰霜巨龙合剂
        [2] = 40212, -- 狂野魔法药水
        [3] = 40211, -- 速度药水
        [4] = 33448, -- 符文法力药水
        [5] = 43015, -- 龙鳞鱼片
        [6] = 34767  -- 爆炒红鲑鱼
    },
    
    -- 物理消耗品
    physical = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 41119, -- 炸弹
        [4] = 43015, -- 鱼肉筵席
        [5] = 43000, -- 龙鳞鱼片
        [6] = 34766  -- 水煮北地蚌背鱼
    },
    
    -- 坦克消耗品
    tank = {
        slot_name = "consumables",
        [1] = 46379, -- 石血合剂
        [2] = 40093, -- 不灭药水
        [3] = 41119, -- 炸弹
        [4] = 43015, -- 鱼肉宴席
        [5] = 43000, -- 龙鳞鱼片
        [6] = 34766  -- 水煮北地蚌背鱼
    },
    
    -- 奶骑消耗品
    paladinHealer = {
        slot_name = "consumables",
        [1] = 44331, -- 闪电疾速药剂
        [2] = 44332, -- 极效思维药剂
        [3] = 40211, -- 速度药水
        [4] = 33448, -- 符文法力药水
        [5] = 34769, -- 帝王鳐鱼片
        [6] = 270314  -- 群体复活卷轴
    },
    
    -- DK消耗品
    deathKnight = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 41119, -- 炸弹
        [4] = 43015, -- 鱼肉筵席
        [5] = 43000, -- 龙鳞鱼片
        [6] = 43005  -- 香辣小龙虾
    },
    
    -- 猎人消耗品
    hunter = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 43015, -- 鱼肉筵席
        [4] = 42999, -- 熏烤龙鳞鱼
        [5] = 34766, -- 水煮北地蚌背鱼
        [6] = 43005  -- 香辣小龙虾
    },
    
    -- 术士消耗品
    warlock = {
        slot_name = "consumables",
        [1] = 46376, -- 冰霜巨龙合剂
        [2] = 40212, -- 狂野魔法药水
        [3] = 40211, -- 速度药水
        [4] = 43015, -- 鱼肉筵席
        [5] = 34767, -- 鱼肉筵席
        [6] = 43005  -- 香辣小龙虾
    },
    
    -- 平衡德消耗品
    balanceDruid = {
        slot_name = "consumables",
        [1] = 46376, -- 冰霜巨龙合剂
        [2] = 40212, -- 狂野魔法药水
        [3] = 40211, -- 速度药水
        [4] = 33448, -- 符文法力药水
        [5] = 43015, -- 鱼肉宴席
        [6] = 34767  -- 爆炒鲑鱼
    },
    
    -- 增强萨消耗品
    enhancementShaman = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 41119, -- 炸弹
        [4] = 43015, -- 鱼肉筵席
        [5] = 42999, -- 熏烤龙鳞鱼
        [6] = 43005  -- 香辣小龙虾
    },
    
    -- 盗贼消耗品
    rogue = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 41119, -- 炸弹
        [4] = 43015, -- 鱼肉筵席
        [5] = 42999, -- 熏烤龙鳞鱼
        [6] = 34754  -- 猛犸肉大餐
    },
    
    -- 猫德消耗品
    feralDruid = {
        slot_name = "consumables",
        [1] = 46377, -- 无尽怒气合剂
        [2] = 40211, -- 速度药水
        [3] = 41119, -- 炸弹
        [4] = 43000, -- 龙鳞鱼片
        [5] = 42999, -- 熏烤龙鳞鱼
        [6] = 42995  -- 犀牛大餐
    },
    
    -- 戒律牧消耗品
    disciplinePriest = {
        slot_name = "consumables",
        [1] = 46376, -- 冰霜巨龙合剂
        [2] = 40212, -- 狂野魔法药水
        [3] = 33448, -- 符文法力药水
        [4] = 43015, -- 鱼肉筵席
        [5] = 34767, -- 爆炒鲑鱼
        [6] = 270314  -- 群体复活卷轴
    }
}

-- 装备信息缓存
local itemInfoCache = {}
local L = LibStub("AceLocale-3.0"):GetLocale("TitanBistooltip", false)



local class = nil
local spec = nil
local phase = nil
local class_index = nil
local spec_index = nil
local phase_index = nil

local class_options = {}
local class_options_to_class = {}

local spec_options = {}
local spec_options_to_spec = {}
local spec_frame = nil
local items = {}
local spells = {}
local main_frame = nil

local controlRefs = {
    dropDownGroup = nil,
    classDropdown = nil,
    specDropdown = nil,
    phaseDropdown = nil,
    scrollFrame = nil
}

local checkmarks = {}

-- 防抖功能
local tooltip_timer = nil
local function debounceTooltip(callback, delay)  
    if tooltip_timer then
        tooltip_timer:Cancel()
        tooltip_timer = nil -- 释放定时器引用
    end
    tooltip_timer = C_Timer.NewTimer(delay, function()
        callback()
        tooltip_timer = nil -- 回调执行后释放定时器
    end)
end
local boemarks = {}

local isHorde = UnitFactionGroup("player") == "Horde"

local itemCache = {}
local factionItemCache = {}
TitanBistooltip_equipmentCache = {}

local function clearCaches()
    itemCache = {}
    factionItemCache = {}
    TitanBistooltip_equipmentCache = {}
    itemInfoCache = {}
end

local function createItemFrame(item_id, size, with_checkmark, original_item_id)
    -- 如果没有提供original_item_id，就用item_id
    original_item_id = original_item_id or item_id
    if item_id < 0 then
        local f = AceGUI:Create("Label")
        return f
    end
    local item_frame = AceGUI:Create("Icon")
    item_frame:SetImageSize(size, size)
    items[item_id] = Item:CreateFromItemID(item_id);

    if (items[item_id]:GetItemID()) then
        items[item_id]:ContinueOnItemLoad(function()
            local ilink = items[item_id]:GetItemLink()
            item_frame:SetImage(items[item_id]:GetItemIcon())
            -- 存储ilink到userdata，避免闭包问题
            item_frame:SetUserData("ilink", ilink)
            item_frame:SetUserData("item_id", item_id)
            
            -- 只有当with_checkmark为true时才检查装备是否存在并显示绿色勾选
            if with_checkmark == true then
                local hasEquipment = false
                -- 对于联盟玩家，检查时用转换后的item_id；对于部落玩家，用original_item_id
                local check_item_id = isHorde and original_item_id or item_id
                
                -- 首先检查TitanBistooltip_char_equipment表
                if TitanBistooltip_char_equipment and TitanBistooltip_char_equipment[check_item_id] ~= nil then
                    hasEquipment = true
                end
                
                -- 然后检查玩家是否实际拥有该装备
                -- 通过遍历玩家的装备栏来检查
                if not hasEquipment then
                    for j = 1, 19 do -- 19个装备栏位
                        local equippedItem
                        if C_PlayerInfo and C_PlayerInfo.GetInventoryItemID then
                            equippedItem = C_PlayerInfo.GetInventoryItemID("player", j)
                        else
                            equippedItem = GetInventoryItemID("player", j)
                        end
                        if equippedItem and equippedItem == check_item_id then
                            hasEquipment = true
                            break
                        end
                    end
                end
                
                if hasEquipment then
                    local checkMark = item_frame.frame:CreateTexture(nil, "OVERLAY")
                    checkMark:SetWidth(32)
                    checkMark:SetHeight(32)
                    checkMark:SetPoint("CENTER", 6, -8)
                    checkMark:SetTexture("Interface\\AddOns\\TitanBistooltip\\checkmark-16.tga")
                    table.insert(checkmarks, checkMark)
                end
            end

            -- 从缓存获取装备信息
            local cachedInfo = itemInfoCache[item_id]
            local bindType
            if cachedInfo then
                bindType = cachedInfo.bindType
            else
                local bindTypeVal
                -- 直接使用 GetItemInfo 获取绑定类型
                _, _, _, _, _, _, _, _, _, _, _, _, _, bindTypeVal = GetItemInfo(item_id)
                bindType = bindTypeVal
                -- 缓存装备信息
                itemInfoCache[item_id] = { bindType = bindType }
            end
            -- 只有当bindType有效且为装备后绑定类型时才显示图标
            if bindType and (bindType == LE_ITEM_BIND_ON_EQUIP or bindType == 2) then
                local boeMark = item_frame.frame:CreateTexture(nil, "OVERLAY")
                boeMark:SetWidth(12)
                boeMark:SetHeight(12)
                boeMark:SetPoint("TOPLEFT",2,-5)
                boeMark:SetTexture("Interface\\Icons\\INV_Misc_Coin_01")
                table.insert(boemarks, boeMark)
            end

            -- 直接在按钮上绑定右键点击事件
            item_frame.frame:RegisterForClicks("LeftButtonUp", "RightButtonUp")
            item_frame.frame:SetScript("OnMouseUp", function(self, button)
                if button == "RightButton" then
                    -- 复制物品名称
                    -- 从缓存获取装备名称
                    local itemName = items[item_id]:GetItemName()
                    if itemName then
                        -- 尝试复制到剪贴板
                        local success = TitanBistooltipAddon:CopyTextToClipboard(itemName)
                    else
                        -- 从缓存获取装备名称
                        local cachedInfo = itemInfoCache[item_id]
                        if cachedInfo and cachedInfo.name then
                            itemName = cachedInfo.name
                        else
                            if C_Item and C_Item.GetItemInfo then
                                local itemInfo = C_Item.GetItemInfo(item_id)
                                if itemInfo then
                                    itemName = itemInfo.name
                                end
                            else
                                itemName = GetItemInfo(item_id)
                            end
                            -- 缓存装备信息
                            if not itemInfoCache[item_id] then
                                itemInfoCache[item_id] = {}
                            end
                            itemInfoCache[item_id].name = itemName
                        end
                        if itemName then
                            -- 尝试复制到剪贴板
                            local success = TitanBistooltipAddon:CopyTextToClipboard(itemName)
                        else
                            DEFAULT_CHAT_FRAME:AddMessage("|cffff0000无法获取物品名称|r")
                        end
                    end
                end
            end)
            
            -- 保持左键点击功能
            item_frame:SetCallback("OnClick", function(widget, event, button)
                local ilink = widget:GetUserData("ilink")
                if button == "LeftButton" and ilink and type(ilink) == "string" and #ilink > 0 then
                    SetItemRef(ilink, ilink, "LeftButton")
                end
            end)
            item_frame:SetCallback("OnEnter", function(widget) 
                debounceTooltip(function()
                    local ilink = widget:GetUserData("ilink")
                    local itemId = widget:GetUserData("item_id")
                    if ilink and type(ilink) == "string" and #ilink > 0 then
                        GameTooltip:ClearLines() -- 清理之前的内容
                        GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE") -- 使用ANCHOR_NONE
                        
                        -- 获取面板位置，自动调整提示框方向
                        local frame = main_frame and main_frame.frame
                        local screenWidth = GetScreenWidth()
                        local frameRight = frame and frame:GetRight() or 0
                        local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                        
                        if smartPosition and frameRight > screenWidth / 2 then
                            -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧，增加偏移距离避免覆盖
                            GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                        else
                            -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧，增加偏移距离避免覆盖
                            GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                        end
                        
                        GameTooltip:SetHyperlink(ilink)
                    else
                        -- 物品信息无法获取，显示错误提示
                        GameTooltip:ClearLines() -- 清理之前的内容
                        GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE") -- 使用ANCHOR_NONE
                        
                        -- 获取面板位置，自动调整提示框方向
                        local frame = main_frame and main_frame.frame
                        local screenWidth = GetScreenWidth()
                        local frameRight = frame and frame:GetRight() or 0
                        local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                        
                        if smartPosition and frameRight > screenWidth / 2 then
                            -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧，增加偏移距离避免覆盖
                            GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                        else
                            -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧，增加偏移距离避免覆盖
                            GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                        end
                        
                        local errorMsg = "|cffff0000无效的物品信息|r"
                        if itemId then
                            errorMsg = "|cffff0000无效的物品信息(ID: " .. itemId .. ")|r"
                        end
                        GameTooltip:SetText(errorMsg)
                        GameTooltip:Show()
                    end
                end, 0.05) -- 50ms延迟
            end)
            item_frame:SetCallback("OnLeave", function(widget) 
                if tooltip_timer then
                    tooltip_timer:Cancel()
                    tooltip_timer = nil
                end
                GameTooltip:Hide()
                GameTooltip:ClearLines() -- 清理内容
            end)
        end)
    else
        -- 物品ID无效时的处理
        item_frame:SetCallback("OnEnter", function(widget)
            debounceTooltip(function()
                GameTooltip:SetOwner(item_frame.frame)
                
                -- 获取面板位置，自动调整提示框方向
                local frame = main_frame and main_frame.frame
                local screenWidth = GetScreenWidth()
                local frameRight = frame and frame:GetRight() or 0
                local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                
                if smartPosition and frameRight > screenWidth / 2 then
                    -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧，增加偏移距离避免覆盖
                    GameTooltip:SetPoint("TOPLEFT", item_frame.frame, "TOPLEFT", -300, -13);
                else
                    -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧，增加偏移距离避免覆盖
                    GameTooltip:SetPoint("TOPRIGHT", item_frame.frame, "TOPRIGHT", 300, -13);
                end
                
                GameTooltip:SetText("|cffff0000无效的物品信息(ID: " .. item_id .. ")|r")
                GameTooltip:Show()
            end, 0.05) -- 50ms延迟
        end)
        item_frame:SetCallback("OnLeave", function(widget)
            if tooltip_timer then
                tooltip_timer:Cancel()
                tooltip_timer = nil
            end
            GameTooltip:Hide()
        end)
    end
    return item_frame
end

local function createSpellFrame(spell_id, size)
    if not spell_id or spell_id < 0 then
        local f = AceGUI:Create("Label")
        return f
    end
    local spell_frame = AceGUI:Create("Icon")
    spell_frame:SetImageSize(size, size)
    
    -- 检查Spell是否可用
    if not Spell then
        -- Spell API不可用，设置错误提示
        spell_frame:SetCallback("OnEnter", function(widget)
            debounceTooltip(function()
                GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE")
                
                -- 获取面板位置，自动调整提示框方向
                local frame = main_frame and main_frame.frame
                local screenWidth = GetScreenWidth()
                local frameRight = frame and frame:GetRight() or 0
                local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                
                if smartPosition and frameRight > screenWidth / 2 then
                    -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧
                    GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                else
                    -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧
                    GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                end
                
                GameTooltip:SetText("|cffff0000Spell API不可用|r")
                GameTooltip:Show()
            end, 0.05) -- 50ms延迟
        end)
        spell_frame:SetCallback("OnLeave", function(widget)
            if tooltip_timer then
                tooltip_timer:Cancel()
                tooltip_timer = nil
            end
            GameTooltip:Hide()
        end)
        return spell_frame
    end
    
    spells[spell_id] = Spell:CreateFromSpellID(spell_id);

    if (spells[spell_id] and spells[spell_id]:GetSpellID()) then
        spells[spell_id]:ContinueOnSpellLoad(function()
            local name, rank, icon, castTime, minRange, maxRange = GetSpellInfo(spell_id)
            if not name then
                -- 法术信息无法获取，设置错误提示回调
                spell_frame:SetCallback("OnEnter", function(widget)
                    debounceTooltip(function()
                        GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE")
                        
                        -- 获取面板位置，自动调整提示框方向
                        local frame = main_frame and main_frame.frame
                        local screenWidth = GetScreenWidth()
                        local frameRight = frame and frame:GetRight() or 0
                        local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                        
                        if smartPosition and frameRight > screenWidth / 2 then
                            -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧
                            GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                        else
                            -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧
                            GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                        end
                        
                        GameTooltip:SetText("|cffff0000无效的法术信息(ID: " .. spell_id .. ")|r")
                        GameTooltip:Show()
                    end, 0.05) -- 50ms延迟
                end)
                spell_frame:SetCallback("OnLeave", function(widget)
                    if tooltip_timer then
                        tooltip_timer:Cancel()
                        tooltip_timer = nil
                    end
                    GameTooltip:Hide()
                end)
                return
            end
            spell_frame:SetImage(icon)
            local link = GetSpellLink(spell_id)
            if link == nil then
                link = "\124cffffd000\124Hspell:" .. spell_id .. "\124h[" .. name .. "]\124h\124r"
            end
            -- 存储link和spellId到userdata，避免闭包问题
            spell_frame:SetUserData("link", link)
            spell_frame:SetUserData("name", name)
            spell_frame:SetUserData("spellId", spell_id)
            -- 直接在按钮上绑定右键点击事件
            spell_frame.frame:RegisterForClicks("LeftButtonUp", "RightButtonUp")
            spell_frame.frame:SetScript("OnMouseUp", function(self, button)
                if button == "RightButton" then
                    -- 复制法术/附魔名称
                    local spellName = spell_frame:GetUserData("name")
                    if spellName then
                        -- 尝试复制到剪贴板
                        local success = TitanBistooltipAddon:CopyTextToClipboard(spellName)
                    else
                        DEFAULT_CHAT_FRAME:AddMessage("|cffff0000无法获取法术/附魔名称|r")
                    end
                end
            end)
            
            -- 保持左键点击功能
            spell_frame:SetCallback("OnClick", function(widget, event, button)
                local link = widget:GetUserData("link")
                if button == "LeftButton" and link and type(link) == "string" and #link > 0 then
                    SetItemRef(link, link, "LeftButton")
                end
            end)
            spell_frame:SetCallback("OnEnter", function(widget)
                debounceTooltip(function()
                    local link = widget:GetUserData("link")
                    local spellId = widget:GetUserData("spellId")
                    if link and type(link) == "string" and #link > 0 then
                        GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE")
                        
                        -- 获取面板位置，自动调整提示框方向
                        local frame = main_frame and main_frame.frame
                        local screenWidth = GetScreenWidth()
                        local frameRight = frame and frame:GetRight() or 0
                        local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                        
                        if smartPosition and frameRight > screenWidth / 2 then
                            -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧
                            GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                        else
                            -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧
                            GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                        end
                        
                        GameTooltip:SetHyperlink(link)
                    else
                        -- 法术信息无法获取，显示错误提示
                        GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE")
                        
                        -- 获取面板位置，自动调整提示框方向
                        local frame = main_frame and main_frame.frame
                        local screenWidth = GetScreenWidth()
                        local frameRight = frame and frame:GetRight() or 0
                        local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                        
                        if smartPosition and frameRight > screenWidth / 2 then
                            -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧
                            GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                        else
                            -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧
                            GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                        end
                        
                        local errorMsg = "|cffff0000无效的法术信息|r"
                        if spellId then
                            errorMsg = "|cffff0000无效的法术信息(ID: " .. spellId .. ")|r"
                        end
                        GameTooltip:SetText(errorMsg)
                        GameTooltip:Show()
                    end
                end, 0.05) -- 50ms延迟
            end)
            spell_frame:SetCallback("OnLeave", function(widget)
                if tooltip_timer then
                    tooltip_timer:Cancel()
                    tooltip_timer = nil
                end
                GameTooltip:Hide()
            end)
        end)
    else
        -- 法术ID无效，设置错误提示
        spell_frame:SetCallback("OnEnter", function(widget)
            debounceTooltip(function()
                GameTooltip:SetOwner(widget.frame, "ANCHOR_NONE")
                
                -- 获取面板位置，自动调整提示框方向
                local frame = main_frame and main_frame.frame
                local screenWidth = GetScreenWidth()
                local frameRight = frame and frame:GetRight() or 0
                local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                
                if smartPosition and frameRight > screenWidth / 2 then
                    -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧
                    GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13);
                else
                    -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧
                    GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13);
                end
                
                GameTooltip:SetText("|cffff0000无效的法术ID: " .. spell_id .. "|r")
                GameTooltip:Show()
            end, 0.05) -- 50ms延迟
        end)
        spell_frame:SetCallback("OnLeave", function(widget)
            if tooltip_timer then
                tooltip_timer:Cancel()
                tooltip_timer = nil
            end
            GameTooltip:Hide()
        end)
    end
    return spell_frame
end

local function createEnhancementsFrame(enhancements, phase, slot_name)
    local frame = AceGUI:Create("SimpleGroup")
    frame:SetLayout("Table")
    frame:SetFullWidth(true)
    frame:SetHeight(50) -- 增加高度以容2个宝石的垂直排列
    frame:SetAutoAdjustHeight(false)
    frame:SetUserData("table", {
        columns = {
            { width = 20 }, -- 第一列：附魔
            { width = 20 }  -- 第二列：宝石
        },
        spaceV = 2,
        spaceH = -2, -- 列间距为-2，平衡显示
        align = "TOP"
    })
    
    -- 创建附魔容器
    local enchantContainer = AceGUI:Create("SimpleGroup")
    enchantContainer:SetLayout("Table")
    enchantContainer:SetFullWidth(true)
    enchantContainer:SetHeight(50) -- 与宝石容器高度一致
    enchantContainer:SetUserData("table", {
        columns = {
            { width = 20 }
        },
        spaceV = 2,
        align = "TOP" -- 上部对齐
    })
    
    -- 创建宝石容器（垂直排列）
    local gemsContainer = AceGUI:Create("SimpleGroup")
    gemsContainer:SetLayout("Table")
    gemsContainer:SetFullWidth(true)
    gemsContainer:SetHeight(50)
    gemsContainer:SetUserData("table", {
        columns = {
            { width = 20 }
        },
        spaceV = 2,
        align = "TOP"
    })
    
    -- 根据阶段决定宝石的最大显示数量
    local maxGems = 2 -- 所有阶段最多显示2个宝石
    
    local gemCount = 0
    
    for i, enhancement in ipairs(enhancements) do
        local size = 16

        -- 头部、肩部、胸部、手部、腰部、腿部、脚部、披风、主手武器、副手、盾牌和护腕的第一个增强归类到附魔容器
        local isEnchantSlot = false
        if (slot_name == "Head" or slot_name == "Shoulder" or slot_name == "Chest" or slot_name == "Hands" or slot_name == "Waist" or slot_name == "Legs" or slot_name == "Feet" or slot_name == "Back" or slot_name == "Weapon" or slot_name == "Off hand" or slot_name == "Ranged" or slot_name == "Wrist") and i == 1 then
            isEnchantSlot = true
        end

        if enhancement and (enhancement.type == "spell" or (isEnchantSlot and enhancement.type == "item")) then -- 附魔（spell类型）或特殊槽位的item类型
            local enchantFrame
            if enhancement.type == "spell" then
                enchantFrame = createSpellFrame(enhancement.id, size)
            else
                enchantFrame = createItemFrame(enhancement.id, size)
            end
            enchantFrame:SetUserData("enchantId", enhancement.id)
            enchantFrame:SetHeight(size)
            enchantFrame:SetWidth(size)
            enchantContainer:AddChild(enchantFrame)
        end
        
        if enhancement and enhancement.type == "item" and not isEnchantSlot and gemCount < maxGems then -- 宝石，排除特殊槽位的item，最多显示maxGems个
            local gemFrame = createItemFrame(enhancement.id, size)
            gemFrame:SetUserData("gemId", enhancement.id)
            gemFrame:SetHeight(size)
            gemFrame:SetWidth(size)
            gemsContainer:AddChild(gemFrame)
            gemCount = gemCount + 1
        end
    end
    
    -- 添加附魔容器
    frame:AddChild(enchantContainer)
    -- 添加宝石容器
    frame:AddChild(gemsContainer)
    
    return frame
end

local function drawItemSlot(slot, phase)
    if not slot then return end
    
    local f = AceGUI:Create("Label")
    -- f:SetText(slot.slot_name)
    -- f:SetFont("Fonts\\FRIZQT__.TTF", 14, "")
    
    -- 根据职业和天赋选择不同的武器槽位翻译
       local slotText = L[slot.slot_name] or slot.slot_name or "Unknown Slot"
    if (class == "Death knight" and spec == "Unholy") or (class == "Hunter") or (class == "Shaman" and spec == "Enhancement") then
        if slot.slot_name == "Weapon" then
            -- 死亡骑士邪恶天赋/猎人/增强萨主手显示为"双手"
            slotText = "双手"
        elseif slot.slot_name == "Off hand" then
            -- 死亡骑士邪恶天赋/猎人/增强萨副手显示为"单手"
            slotText = "单手"
        end
    end
    
    f:SetText(slotText)
    spec_frame:AddChild(f)
    spec_frame:AddChild(createEnhancementsFrame(slot.enhs or {}, phase, slot.slot_name or "Unknown"))
    
    -- 获取隐藏传说装备配置
    local hideLegendary = TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.hide_legendary_items == true
    
    -- 第一步：收集装备到渲染列表（过滤传说装备）
    local originalCount = #slot
    local finalRenderList = {}
    
    for i, original_item_id in ipairs(slot) do
        -- 保存原始item_id用于装备检查
        local item_id = original_item_id
        
        -- 使用缓存来避免重复计算物品映射
        local cacheKey = original_item_id
        if not isHorde then
            if factionItemCache[cacheKey] == nil then
                factionItemCache[cacheKey] = TitanBistooltip_horde_to_ali[original_item_id] or original_item_id
            end
            item_id = factionItemCache[cacheKey]
        end
        
        -- 如果启用了隐藏传说装备选项
        if hideLegendary then
            -- 检查当前装备是否是传说装备
            local isLegendary = false
            -- 使用GetItemInfo同步获取物品名称
            local itemName = GetItemInfo(item_id)
            if itemName and itemName ~= "" and TitanBistooltip_legendary_names[itemName] then
                isLegendary = true
            end
            
            -- 如果是传说装备，跳过
            if not isLegendary then
                table.insert(finalRenderList, {
                    item_id = item_id,
                    original_item_id = original_item_id
                })
            end
        else
            table.insert(finalRenderList, {
                item_id = item_id,
                original_item_id = original_item_id
            })
        end
    end
    
    -- 第二步：渲染过滤后的列表
    for _, itemData in ipairs(finalRenderList) do
        spec_frame:AddChild(createItemFrame(itemData.item_id, 40, true, itemData.original_item_id))
    end
    
    -- 第三步：补齐空位，保持每个槽位占8列
    local filteredCount = #finalRenderList
    local missingCount = originalCount - filteredCount
    for i = 1, missingCount do
        local emptyLabel = AceGUI:Create("Label")
        emptyLabel:SetText("")
        emptyLabel:SetWidth(48)
        spec_frame:AddChild(emptyLabel)
    end
end

local function drawTableHeader(frame)
    local f = AceGUI:Create("Label")
    -- f:SetText("Slot")
    -- f:SetFont("Fonts\\FRIZQT__.TTF", 14, "")
    f:SetText(L["slot"])
    local color = 0.6
    f:SetColor(color, color, color)
    frame:AddChild(f)
    frame:AddChild(AceGUI:Create("Label"))
    for i = 1, 6 do
        f = AceGUI:Create("Label")
        f:SetText("Top " .. i)
        f:SetColor(color, color, color)
        frame:AddChild(f)
    end
end

local function saveData()
    TitanBistooltipAddon.db.global.class_index = class_index
    TitanBistooltipAddon.db.global.spec_index = spec_index
    TitanBistooltipAddon.db.global.phase_index = phase_index
end

local function clearCheckMarks()
    for key, value in ipairs(checkmarks) do
        value:SetTexture(nil)
    end
    checkmarks = {}
end

local function clearBoeMarks()
    for key, value in ipairs(boemarks) do
        value:SetTexture(nil)
    end
    boemarks = {}
end

local function drawSpecData()
    clearCheckMarks()
    clearBoeMarks()
    clearCaches()
    saveData()
    items = {}
    spells = {}
    
    -- 确保spec_frame存在
    if not spec_frame then
        spec_frame = controlRefs.scrollFrame
    end
    
    if spec_frame then
        spec_frame:ReleaseChildren()
        drawTableHeader(spec_frame)
        if not spec or not phase or not class then
            return
        end
        
        local slots = TitanBistooltip_bislists[class][spec][phase]
        
        if main_frame and main_frame.frame and main_frame.frame.SetResizeBounds then
            main_frame.frame:SetResizeBounds(435, 300, 435, 880)
        end
        
        if slots then
            -- 使用分批处理来避免脚本执行时间过长
            local currentSlot = 1
            local batchSize = 7 -- 每批处理7个槽位
            
            local function processBatch()
                local endSlot = math.min(currentSlot + batchSize - 1, #slots)
                
                for i = currentSlot, endSlot do
                    drawItemSlot(slots[i], phase)
                end
                
                currentSlot = endSlot + 1
                
                if currentSlot <= #slots then
                    -- 继续处理下一批次
                    C_Timer.After(0.1, processBatch)
                else
                    -- 处理完所有常规槽位后，添加消耗品槽位
                    C_Timer.After(0.1, function()
                        -- 根据职业和专精类型添加不同的消耗品槽位
                        local consumableGroups = {}
                        
                        -- 从Consumables.lua加载消耗品数据
                        local casterConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.caster
                        local physicalConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.physical
                        local tankConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.tank
                        local paladinHealerConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.paladinHealer
                        local deathKnightConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.deathKnight
                        local hunterConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.hunter
                        local warlockConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.warlock
                        local balanceDruidConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.balanceDruid
                        local enhancementShamanConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.enhancementShaman
                        local rogueConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.rogue
                        local feralDruidConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.feralDruid
                        local disciplinePriestConsumables = TitanBistooltip_consumables and TitanBistooltip_consumables.disciplinePriest
                        
                        -- 根据职业和专精类型添加相应的消耗品槽位
                        local isCaster = false
                        local isPhysical = false
                        local isTank = false
                        local isHealer = false
                        
                        -- 法系职业天赋
                        local casterSpecs = {
                            "Balance", "Elemental", "Arcane", "Fire", "Frost", "Shadow", 
                            "Affliction", "Demonology", "Destruction", "Holy", "Discipline", "Restoration"
                        }
                        
                        -- 物理职业天赋
                        local physicalSpecs = {
                            "Feral dps", "Beast mastery", "Marksmanship", "Survival", 
                            "Assassination", "Combat", "Subtlety", "Enhancement", 
                            "Arms", "Fury", "Retribution"
                        }
                        
                        -- 坦克职业天赋
                        local tankSpecs = {
                            "Blood tank", "Feral tank", "Protection"
                        }
                        
                        -- 检查当前专精类型
                        for _, casterSpec in ipairs(casterSpecs) do
                            if spec == casterSpec then
                                isCaster = true
                                break
                            end
                        end
                        
                        for _, physicalSpec in ipairs(physicalSpecs) do
                            if spec == physicalSpec then
                                isPhysical = true
                                break
                            end
                        end
                        
                        for _, tankSpec in ipairs(tankSpecs) do
                            if spec == tankSpec then
                                isTank = true
                                break
                            end
                        end
                        
                        -- 治疗职业天赋
                        if spec == "Holy" or spec == "Discipline" or spec == "Restoration" then
                            isHealer = true
                        end
                        
                        -- 根据专精类型添加相应的消耗品槽位
                        if class == "Paladin" and spec == "Holy" then
                            -- 奶骑
                            table.insert(consumableGroups, paladinHealerConsumables)
                        elseif class == "Death knight" and spec == "Blood tank" then
                            -- DK鲜血坦克天赋归类到坦克槽位
                            table.insert(consumableGroups, tankConsumables)
                        elseif class == "Death knight" then
                            -- DK其他天赋
                            table.insert(consumableGroups, deathKnightConsumables)
                        elseif class == "Hunter" then
                            -- 猎人
                            table.insert(consumableGroups, hunterConsumables)
                        elseif class == "Warlock" then
                            -- 术士
                            table.insert(consumableGroups, warlockConsumables)
                        elseif class == "Druid" and spec == "Balance" then
                            -- 平衡德
                            table.insert(consumableGroups, balanceDruidConsumables)
                        elseif class == "Druid" and spec == "Feral dps" then
                            -- 野性输出
                            table.insert(consumableGroups, feralDruidConsumables)
                        elseif class == "Druid" and spec == "Feral tank" then
                            -- 野性坦克归类到坦克槽位
                            table.insert(consumableGroups, tankConsumables)
                        elseif class == "Druid" and spec == "Restoration" then
                            -- 恢复德归类到法系槽位
                            table.insert(consumableGroups, casterConsumables)
                        elseif class == "Rogue" then
                            -- 盗贼
                            table.insert(consumableGroups, rogueConsumables)
                        elseif class == "Shaman" and spec == "Enhancement" then
                            -- 增强槽位
                            table.insert(consumableGroups, enhancementShamanConsumables)
                        elseif class == "Priest" and spec == "Discipline" then
                            -- 戒律槽位
                            table.insert(consumableGroups, disciplinePriestConsumables)
                        elseif isCaster then
                            -- 法系
                            table.insert(consumableGroups, casterConsumables)
                        elseif isPhysical then
                            -- 物理
                            table.insert(consumableGroups, physicalConsumables)
                        elseif isTank then
                            -- 坦克
                            table.insert(consumableGroups, tankConsumables)
                        else
                            -- 默认添加所有消耗品槽位
                            table.insert(consumableGroups, casterConsumables)
                            table.insert(consumableGroups, physicalConsumables)
                            table.insert(consumableGroups, tankConsumables)
                        end
                        
                        -- 显示所有消耗品槽位
                        for _, consumablesSlot in ipairs(consumableGroups) do
                            drawItemSlot(consumablesSlot, phase)
                        end
                    end)
                end
            end
            
            -- 开始分批处理
            processBatch()
        end
    end
end

local function buildClassDict()
    class_options = {}
    class_options_to_class = {}
    if TitanBistooltip_classes then
        for ci, class in ipairs(TitanBistooltip_classes) do
            if class and class.name then
                local icon = ""
                if TitanBistooltip_spec_icons and TitanBistooltip_spec_icons[class.name] and TitanBistooltip_spec_icons[class.name].classIcon then
                    icon = "|T" .. TitanBistooltip_spec_icons[class.name].classIcon .. ":14|t "
                end
                local option_name = icon .. (L[class.name] or class.name)
                table.insert(class_options, option_name)
                class_options_to_class[option_name] = { name = class.name, i = ci }
            end
        end
    end
end

local function buildSpecsDict(class_i)
    spec_options = {}
    spec_options_to_spec = {}
    if TitanBistooltip_classes and TitanBistooltip_classes[class_i] and TitanBistooltip_classes[class_i].specs then
        local class = TitanBistooltip_classes[class_i].name
        for si, spec in ipairs(TitanBistooltip_classes[class_i].specs) do
            if spec and class then
                local icon = ""
                if TitanBistooltip_spec_icons and TitanBistooltip_spec_icons[class] and TitanBistooltip_spec_icons[class][spec] then
                    icon = "|T" .. TitanBistooltip_spec_icons[class][spec] .. ":14|t "
                end
                local option_name = icon .. (L[spec] or spec)
                table.insert(spec_options, option_name)
                spec_options_to_spec[option_name] = spec
            end
        end
    end
end

local function loadData()
    if TitanBistooltipAddon.db and TitanBistooltipAddon.db.global then
        class_index = TitanBistooltipAddon.db.global.class_index
        spec_index = TitanBistooltipAddon.db.global.spec_index
        -- 从设置中读取默认阶段
        local defaultPhase = TitanBistooltipAddon.db.global.default_phase or "P3"
        -- 确保TitanBistooltip_phases被正确初始化
        if not TitanBistooltip_phases or #TitanBistooltip_phases == 0 then
            TitanBistooltip_phases = TitanBistooltip_Titan_phases or { "PR" , "P1" , "P2" , "P3" , "P4" }
        end
        -- 找到默认阶段在TitanBistooltip_phases中的索引
        phase_index = 1
        local found = false
        for i, phase in ipairs(TitanBistooltip_phases) do
            if phase == defaultPhase then
                phase_index = i
                found = true
                break
            end
        end
        -- 如果在过滤后的阶段列表中找不到默认阶段，使用第一个阶段
        if not found then
            phase_index = 1
        end
        TitanBistooltipAddon.db.global.phase_index = phase_index
        if class_index and class_options and class_options[class_index] and class_options_to_class and class_options_to_class[class_options[class_index]] then
            class = class_options_to_class[class_options[class_index]].name
            buildSpecsDict(class_index)
        end
        if spec_index and spec_options and spec_options[spec_index] and spec_options_to_spec and spec_options_to_spec[spec_options[spec_index]] then
            spec = spec_options_to_spec[spec_options[spec_index]]
        end
        -- 确保phase变量被正确设置
        if phase_index and TitanBistooltip_phases and #TitanBistooltip_phases > 0 then
            phase = TitanBistooltip_phases[phase_index]
        else
            -- 如果TitanBistooltip_phases还没有被初始化，直接使用默认阶段
            phase = defaultPhase
        end
    end
end

local function drawDropdowns()
    -- 复用或创建下拉菜单组
    if not controlRefs.dropDownGroup then
        controlRefs.dropDownGroup = AceGUI:Create("SimpleGroup")
        controlRefs.dropDownGroup:SetLayout("Table")
        controlRefs.dropDownGroup:SetUserData("table", {
            columns = {
                130, 160, 80 },
            space = 3,
            align = "BOTTOMLEFT"
        })
        controlRefs.dropDownGroup:SetFullWidth(true)
        controlRefs.dropDownGroup:SetHeight(40) -- 设置固定高度，方便计算可用高度
        main_frame:AddChild(controlRefs.dropDownGroup)
        
        -- 存储下拉菜单组的引用，用于后续计算高度
        main_frame.dropDownGroup = controlRefs.dropDownGroup
    else
        controlRefs.dropDownGroup:ReleaseChildren()
    end

    -- 复用或创建职业下拉菜单
    if not controlRefs.classDropdown then
        controlRefs.classDropdown = AceGUI:Create("Dropdown")
        controlRefs.classDropdown:SetCallback("OnValueChanged", function(_, _, key)
            class_index = key
            class = class_options_to_class[class_options[key]].name
            
            -- 清除缓存，确保数据正确加载
            clearCaches()

            controlRefs.specDropdown:SetDisabled(false)
            buildSpecsDict(key)
            controlRefs.specDropdown:SetList(spec_options)
            controlRefs.specDropdown:SetValue(1)
            spec_index = 1
            spec = spec_options_to_spec[spec_options[1]]
            drawSpecData()
        end)
    end

    -- 复用或创建专精下拉菜单
    if not controlRefs.specDropdown then
        controlRefs.specDropdown = AceGUI:Create("Dropdown")
        controlRefs.specDropdown:SetCallback("OnValueChanged", function(_, _, key)
            spec_index = key
            spec = spec_options_to_spec[spec_options[key]]
            drawSpecData()
        end)
    end

    -- 复用或创建阶段下拉菜单
    if not controlRefs.phaseDropdown then
        controlRefs.phaseDropdown = AceGUI:Create("Dropdown")
        controlRefs.phaseDropdown:SetCallback("OnValueChanged", function(_, _, key)
            phase_index = key
            phase = TitanBistooltip_phases[key]
            drawSpecData()
        end)
    end

    controlRefs.specDropdown:SetDisabled(true)

    controlRefs.classDropdown:SetList(class_options)
    controlRefs.phaseDropdown:SetList(TitanBistooltip_phases)

    controlRefs.dropDownGroup:AddChild(controlRefs.classDropdown)
    controlRefs.dropDownGroup:AddChild(controlRefs.specDropdown)
    controlRefs.dropDownGroup:AddChild(controlRefs.phaseDropdown)

    -- 移除不必要的空白填充
    -- local fillerFrame = AceGUI:Create("Label")
    -- fillerFrame:SetText(" ")
    -- main_frame:AddChild(fillerFrame)

    controlRefs.classDropdown:SetValue(class_index)
    if (class_index) then
        buildSpecsDict(class_index)
        controlRefs.specDropdown:SetList(spec_options)
        controlRefs.specDropdown:SetDisabled(false)
    end
    controlRefs.specDropdown:SetValue(spec_index)
    controlRefs.phaseDropdown:SetValue(phase_index)
end

local function createSpecFrame()
    -- 复用或创建滚动框架
    if not controlRefs.scrollFrame then
        controlRefs.scrollFrame = AceGUI:Create("ScrollFrame")
        controlRefs.scrollFrame:SetLayout("Table")
        controlRefs.scrollFrame:SetUserData("table", {
            columns = {
                { width = 50 },
                { width = 30 },
                { width = 48 },
                { width = 48 },
                { width = 48 },
                { width = 48 },
                { width = 48 },
                { width = 48 } },
            space = 1,
            align = "middle"
        })
        controlRefs.scrollFrame:SetFullWidth(true)
        controlRefs.scrollFrame:SetFullHeight(false)
        controlRefs.scrollFrame:SetAutoAdjustHeight(false)
        main_frame:AddChild(controlRefs.scrollFrame)
    end
    spec_frame = controlRefs.scrollFrame
    
    -- 添加面板大小变化回调，动态调整滚动框架高度
    local function updateScrollFrameHeight()
        if main_frame and main_frame.frame and main_frame.dropDownGroup and controlRefs.scrollFrame then
            local frameHeight = main_frame.frame:GetHeight()
            local titleBarHeight = 24 -- 标题栏高度
            local dropDownHeight = 40 -- 下拉菜单组高度
            local statusBarHeight = 24 -- 状态栏高度
            local padding = 10 -- 额外 padding
            
            local availableHeight = frameHeight - titleBarHeight - dropDownHeight - statusBarHeight - padding
            availableHeight = math.max(200, availableHeight) -- 确保最小高度
            
            controlRefs.scrollFrame:SetHeight(availableHeight)
        end
    end
    
    -- 初始计算一次滚动框架高度
    updateScrollFrameHeight()
    
    -- 添加OnSizeChanged回调
    main_frame.frame:SetScript("OnSizeChanged", updateScrollFrameHeight)
    
    -- 确保主面板的拉伸功能正常工作
    if main_frame and main_frame.frame and main_frame.frame.SetResizeBounds then
        main_frame.frame:SetResizeBounds(435, 300, 435, 800)
    end
end

function TitanBistooltipAddon:reloadData()
    buildClassDict()
    
    -- 检查数据库是否已初始化
    if not TitanBistooltipAddon.db or not TitanBistooltipAddon.db.global then
        return
    end
    
    class_index = TitanBistooltipAddon.db.global.class_index or 1
    spec_index = TitanBistooltipAddon.db.global.spec_index or 1
    phase_index = TitanBistooltipAddon.db.global.phase_index or 1

    -- 检查索引值是否有效
    if class_index and class_options and class_options[class_index] and class_options_to_class and class_options_to_class[class_options[class_index]] then
        class = class_options_to_class[class_options[class_index]].name
        buildSpecsDict(class_index)
    else
        class_index = 1
        class = class_options_to_class[class_options[1]].name
        buildSpecsDict(1)
    end
    
    spec = spec_options_to_spec[spec_options[spec_index]]
    phase = TitanBistooltip_phases[phase_index]
    
    -- 确保主面板的拉伸功能正常工作
    if main_frame and main_frame.frame and main_frame.frame.SetResizeBounds then
        main_frame.frame:SetResizeBounds(435, 300, 435, 800)
    end

    if main_frame then
        controlRefs.phaseDropdown:SetList(TitanBistooltip_phases)
        controlRefs.classDropdown:SetList(class_options)
        controlRefs.specDropdown:SetList(spec_options)

        controlRefs.classDropdown:SetValue(class_index)
        controlRefs.specDropdown:SetValue(spec_index)
        controlRefs.phaseDropdown:SetValue(phase_index)

        drawSpecData()
        main_frame:SetStatusText(TitanBistooltip_source_to_url[TitanBistooltipAddon.db.global["data_source"]])
        
        -- 确保状态栏长度保持一致
        if main_frame.statustext and main_frame.statustext:GetParent() then
            local statusbg = main_frame.statustext:GetParent()
            statusbg:SetPoint("BOTTOMRIGHT", -250, 15)
        end
        
        -- 确保content区域的锚点设置保持一致
        if main_frame.content then
            main_frame.content:SetPoint("BOTTOMRIGHT", -17, 40)
        end
        
        -- 更新毕业装备框体
        if TitanBistooltipAddon.updateMaxedFrame then
            TitanBistooltipAddon:updateMaxedFrame()
        end
    end
end

function TitanBistooltipAddon:createMainFrame()
    if main_frame then
        -- 如果框架已经存在，显示它并重新设置拉伸功能
        main_frame.frame:Show()
        -- 重新设置拉伸功能，避免偶尔失
        if main_frame.frame and main_frame.frame.SetResizeBounds then
            main_frame.frame:SetResizeBounds(435, 300, 435, 800)
        end
        return
    end
    
    -- 确保全局变量与配置文件同步
    loadData()
    
    main_frame = AceGUI:Create("Frame")
    main_frame:SetWidth(435)
    main_frame:SetHeight(500)
    main_frame.frame:SetResizeBounds(435, 300, 435, 880)
    
    -- 设置标题
    local addonNameAndVersion = "TitanBistooltip v" .. (TitanBistooltipAddon.Version or "2.14")
    main_frame:SetTitle(addonNameAndVersion)
    
    -- 设置main_frame引用到Core.lua
    if TitanBistooltipAddon and TitanBistooltipAddon.setMainFrameRef then
        TitanBistooltipAddon:setMainFrameRef(main_frame)
    end
    
    -- 重置面板位置到默认位置
    local function resetFramePosition(frame)
        local screenWidth = GetScreenWidth()
        local screenHeight = GetScreenHeight()
        local frameWidth = frame:GetWidth()
        local frameHeight = frame:GetHeight()
        local rightHalfCenterX = screenWidth * 3/4
        local centerY = screenHeight / 2
        
        -- 确保默认位置在游戏界面内
        rightHalfCenterX = math.max(0, math.min(rightHalfCenterX, screenWidth - frameWidth))
        centerY = math.max(0, math.min(centerY, screenHeight - frameHeight))
        
        frame:ClearAllPoints()
        frame:SetPoint("CENTER", UIParent, "BOTTOMLEFT", rightHalfCenterX, centerY)
    end
    
    -- 重置面板位置
    resetFramePosition(main_frame.frame)
    
    -- 当面板显示时，重置位置
    main_frame.frame:HookScript("OnShow", function(self)
        resetFramePosition(self)
    end)
    
    -- 确保面板在游戏界面内
    local function ensureFrameInBounds(frame)
        local screenWidth = GetScreenWidth()
        local screenHeight = GetScreenHeight()
        local frameWidth = frame:GetWidth()
        local frameHeight = frame:GetHeight()
        
        -- 获取当前位置
        local point, relativeTo, relativePoint, x, y = frame:GetPoint()
        
        -- 计算新的位置，确保框架不会移出游戏界面
        local newX = x
        local newY = y
        
        -- 限制左右边界
        if newX < 0 then
            newX = 0
        elseif newX > screenWidth - frameWidth then
            newX = screenWidth - frameWidth
        end
        
        -- 限制上下边界
        if newY < 0 then
            newY = 0
        elseif newY > screenHeight - frameHeight then
            newY = screenHeight - frameHeight
        end
        
        -- 如果位置有变化，更新位置
        if newX ~= x or newY ~= y then
            frame:ClearAllPoints()
            frame:SetPoint(point, relativeTo, relativePoint, newX, newY)
        end
    end
    
    -- 确保初始位置在游戏界面内
    ensureFrameInBounds(main_frame.frame)
    
    -- 当面板显示时，确保位置在游戏界面内
    main_frame.frame:HookScript("OnShow", function(self)
        ensureFrameInBounds(self)
    end)

    --main_frame.frame:SetScript("OnKeyDown", function(self, key)
    --    if key == "ESCAPE" then
    --        TitanBistooltipAddon:closeMainFrame()
    --    end
    --end)
    --main_frame.frame:SetPropagateKeyboardInput(false)

    main_frame:SetCallback("OnClose", function(widget)
        -- 当框架关闭时，只隐藏它，不销毁它
        widget.frame:Hide()
    end)
    
    main_frame:SetCallback("OnMove", function(widget)
        local frame = widget.frame
        local screenWidth = GetScreenWidth()
        local screenHeight = GetScreenHeight()
        local frameWidth = frame:GetWidth()
        local frameHeight = frame:GetHeight()
        
        -- 获取当前位置
        local point, relativeTo, relativePoint, x, y = frame:GetPoint()
        
        -- 计算新的位置，确保框架不会移出游戏界面
        local newX = x
        local newY = y
        
        -- 限制左右边界
        if newX < 0 then
            newX = 0
        elseif newX > screenWidth - frameWidth then
            newX = screenWidth - frameWidth
        end
        
        -- 限制上下边界
        if newY < 0 then
            newY = 0
        elseif newY > screenHeight - frameHeight then
            newY = screenHeight - frameHeight
        end
        
        -- 如果位置有变化，更新位置
        if newX ~= x or newY ~= y then
            frame:ClearAllPoints()
            frame:SetPoint(point, relativeTo, relativePoint, newX, newY)
        end
    end)
    main_frame:SetLayout("List")
    main_frame:SetStatusText(TitanBistooltip_source_to_url[TitanBistooltipAddon.db.global["data_source"]])
    
    -- 修改状态栏长度，缩放1/3
    if main_frame.statustext and main_frame.statustext:GetParent() then
        local statusbg = main_frame.statustext:GetParent()
        statusbg:SetPoint("BOTTOMRIGHT", -250, 15)
    end
    
    -- 恢复content区域的默认锚点设置
    if main_frame.content then
        main_frame.content:SetPoint("BOTTOMRIGHT", -17, 40)
    end
    
    local frame = main_frame.frame
    frame:SetScript("OnMouseDown", nil)
    frame:SetScript("OnMouseUp", nil)
    
    -- 添加阶段毕业装备按钮
        if main_frame.frame then
            -- 查找关闭按钮
            local closeButton = nil
            for _, child in ipairs({main_frame.frame:GetChildren()}) do
                if child:GetObjectType() == "Button" and child:GetText() == CLOSE then
                    closeButton = child
                    -- 修改关闭按钮宽度
                    closeButton:SetWidth(80)
                    break
                end
            end
            
            -- 创建阶段毕业装备按钮
            if closeButton then
                -- 创建毕业装备按钮
                local bisButton = CreateFrame("Button", nil, main_frame.frame, "UIPanelButtonTemplate")
                bisButton:SetPoint("RIGHT", closeButton, "LEFT", -15, 0)
                bisButton:SetHeight(20)
                bisButton:SetWidth(70)
                bisButton:SetText("毕业配装")
                bisButton:SetScript("OnClick", function()
                    if TitanBistooltipAddon and TitanBistooltipAddon.showMaxedFrame then
                        TitanBistooltipAddon:showMaxedFrame()
                    end
                end)
                -- 设置按钮透明度
                if bisButton:GetNormalTexture() then
                    bisButton:GetNormalTexture():SetAlpha(0.5)
                end
                if bisButton:GetPushedTexture() then
                    bisButton:GetPushedTexture():SetAlpha(0.5)
                end
                if bisButton:GetHighlightTexture() then
                    bisButton:GetHighlightTexture():SetAlpha(0.5)
                end
                main_frame.bisButton = bisButton
                
                -- 创建设置按钮
                local gearButton = CreateFrame("Button", nil, main_frame.frame, "UIPanelButtonTemplate")
                gearButton:SetSize(50, 20)
                gearButton:SetPoint("RIGHT", bisButton, "LEFT", -10, 0)
                gearButton:SetText("设置")
                gearButton:SetScript("OnEnter", function(self)
                    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
                    GameTooltip:SetText("点击进入设置界面")
                    GameTooltip:Show()
                end)
                gearButton:SetScript("OnLeave", function(self)
                    GameTooltip:Hide()
                end)
                gearButton:SetScript("OnClick", function(self)
                    -- 点击进入设置界面
                    TitanBistooltipAddon:openConfigDialog()
                end)
                -- 设置按钮透明度
                if gearButton:GetNormalTexture() then
                    gearButton:GetNormalTexture():SetAlpha(0.5)
                end
                if gearButton:GetPushedTexture() then
                    gearButton:GetPushedTexture():SetAlpha(0.5)
                end
                if gearButton:GetHighlightTexture() then
                    gearButton:GetHighlightTexture():SetAlpha(0.5)
                end
                main_frame.gearButton = gearButton
                
                -- 设置关闭按钮透明度
                if closeButton:GetNormalTexture() then
                    closeButton:GetNormalTexture():SetAlpha(0.5)
                end
                if closeButton:GetPushedTexture() then
                    closeButton:GetPushedTexture():SetAlpha(0.5)
                end
                if closeButton:GetHighlightTexture() then
                    closeButton:GetHighlightTexture():SetAlpha(0.5)
                end
            end
            
            local xButton = CreateFrame("Button", nil, main_frame.frame, "UIPanelCloseButton")
            xButton:SetPoint("TOPRIGHT", main_frame.frame, "TOPRIGHT", -2, -2)
            xButton:SetFrameLevel(main_frame.frame:GetFrameLevel() + 2)
            xButton:SetHitRectInsets(0, 0, 0, 0)
            xButton:SetScript("OnClick", function(self)
                main_frame.frame:Hide()
            end)
            main_frame.xButton = xButton
        end
    
    drawDropdowns()
    createSpecFrame()
    drawSpecData()
end

function TitanBistooltipAddon:closeMainFrame()
    if main_frame then
        main_frame.frame:Hide()
        return
    end
end

function TitanBistooltipAddon:ToggleBisListFrame()
    if main_frame and main_frame.frame:IsVisible() then
        main_frame.frame:Hide()
    else
        TitanBistooltipAddon:createMainFrame()
        -- 确保拉伸功能正常工作
        if main_frame and main_frame.frame and main_frame.frame.SetResizeBounds then
            main_frame.frame:SetResizeBounds(435, 300, 435, 800)
        end
    end
end

function TitanBistooltipAddon:showPhaseBISFrame()
    -- 检查是否已经存在阶段毕业装备框体
    if TitanBistooltipAddon.phaseBISFrame then
        TitanBistooltipAddon.phaseBISFrame.frame:Show()
        return
    end
    
    -- 创建阶段毕业装备框体
    local frame = AceGUI:Create("Frame")
    frame:SetWidth(500)
    frame:SetHeight(400)
    frame:SetTitle("阶段毕业装备 - " .. (class or "Unknown") .. " " .. (spec or "Unknown") .. " " .. (phase or "Unknown"))
    frame:SetLayout("List")
    frame:SetCallback("OnClose", function(widget)
        widget.frame:Hide()
    end)
    
    -- 创建滚动框架
    local scrollFrame = AceGUI:Create("ScrollFrame")
    scrollFrame:SetLayout("Table")
    scrollFrame:SetUserData("table", {
        columns = {
            { width = 80 },
            { width = 50 },
            { width = 50 },
            { width = 50 },
            { width = 50 },
            { width = 50 },
            { width = 50 }
        },
        space = 1,
        align = "middle"
    })
    scrollFrame:SetFullWidth(true)
    scrollFrame:SetFullHeight(true)
    frame:AddChild(scrollFrame)
    
    -- 添加表头
    local headerLabel = AceGUI:Create("Label")
    headerLabel:SetText("部位")
    headerLabel:SetColor(1, 1, 0)
    scrollFrame:AddChild(headerLabel)
    
    for i = 1, 6 do
        local headerLabel = AceGUI:Create("Label")
        headerLabel:SetText("Top " .. i)
        headerLabel:SetColor(1, 1, 0)
        scrollFrame:AddChild(headerLabel)
    end
    
    -- 添加每个部位的BIS装备
    if TitanBistooltip_bislists[class] and TitanBistooltip_bislists[class][spec] and TitanBistooltip_bislists[class][spec][phase] then
        local slots = TitanBistooltip_bislists[class][spec][phase]
        
        for _, slot in ipairs(slots) do
            -- 添加部位名称
            local slotLabel = AceGUI:Create("Label")
            slotLabel:SetText(L[slot.slot_name])
            scrollFrame:AddChild(slotLabel)
            
            -- 添加每个位置的装备
            for i = 1, 6 do
                local itemId = slot[i]
                if itemId and itemId > 0 then
                    local itemFrame = createItemFrame(itemId, 40)
                    scrollFrame:AddChild(itemFrame)
                else
                    local emptyLabel = AceGUI:Create("Label")
                    scrollFrame:AddChild(emptyLabel)
                end
            end
        end
    end
    
    -- 保存框体引用
    TitanBistooltipAddon.phaseBISFrame = frame
end

function TitanBistooltipAddon:initBislists()
    buildClassDict()
    loadData()
    LibStub("AceConsole-3.0"):RegisterChatCommand("titanbistooltip", function()
        TitanBistooltipAddon:createMainFrame()
    end)
    LibStub("AceConsole-3.0"):RegisterChatCommand("bis", function()
        TitanBistooltipAddon:createMainFrame()
    end)
end
