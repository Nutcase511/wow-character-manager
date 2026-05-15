-- 快跑兄弟的属性数值转化百分比功能、自动比较装备功能
-- 玩家信息（延迟获取）
local playerClass = nil

-- WLK 版本的急速等级加成职业
-- 圣骑士、死亡骑士、萨满、德鲁伊获得30%额外近战急速
local ExtraHasteClasses = {
    PALADIN = true,
    DEATHKNIGHT = true,
    SHAMAN = true,
    DRUID = true,
}

-- Level 80 rating base (WLK/时光服版本)
local RatingBase = {
    -- 防御属性
    ["DefenseRating"] = 1.5,
    ["DodgeRating"] = 13.8,
    ["ParryRating"] = 13.8,
    ["BlockRating"] = 5,
    -- 命中属性
    ["HitRating"] = 10,
    ["RangedHitRating"] = 10,
    ["SpellHitRating"] = 8,
    -- 暴击属性
    ["CritRating"] = 14,
    ["RangedCritRating"] = 14,
    ["SpellCritRating"] = 14,
    -- PVP属性
    ["ResilienceRating"] = 28.75,
    -- 急速属性（运行时计算）
    ["HasteRating"] = nil,
    ["RangedHasteRating"] = 10,
    ["SpellHasteRating"] = 10,
    -- 精准属性
    ["ExpertiseRating"] = 2.5,
    -- 护甲穿透属性
    ["ArmorPenetrationRating"] = 4.69512176513672 / 1.1,
}

-- 等级系数表 (用于属性转化)
local RatingScalars = {
    0.03846150, 0.03846150, 0.03846150, 0.03846150,  0.03846150,  0.03846150,  0.03846150,  0.03846150,  0.03846150,  0.03846150,
    0.05769232, 0.07692309, 0.09615381, 0.11538458,  0.13461540,  0.15384622,  0.17307690,  0.19230772,  0.21153854,  0.23076922,
    0.24999999, 0.26923081, 0.28846148, 0.30769230,  0.32692312,  0.34615375,  0.36538462,  0.38461539,  0.40384621,  0.42307689,
    0.44230761, 0.46153843, 0.48076930, 0.50000002,  0.51923075,  0.53846147,  0.55769229,  0.57692302,  0.59615379,  0.61538461,
    0.63461533, 0.65384615, 0.67307692, 0.69230765,  0.71153847,  0.73076929,  0.74999996,  0.76923078,  0.78846160,  0.80769228,
    0.82692315, 0.84615392, 0.86538460, 0.88461537,  0.90384624,  0.92307691,  0.94230768,  0.96153855,  0.98076923,  1.00000000,
    1.03797464, 1.07894744, 1.12328768, 1.17142849,  1.22388062,  1.28125003,  1.34426230,  1.41379307,  1.49090911,  1.57692297,
    1.69669417, 1.82556218, 1.96421831, 2.11340541,  2.27392361,  2.44663375,  2.63246166,  2.83240353,  3.04753145,  3.27899897,
    4.30560143, 5.65397461, 7.42754553, 9.75272320, 12.80571629, 16.25000000, 20.78000000, 26.40000000, 33.69000000, 42.79000000,
}

-- PVP属性特殊系数
local PvpScalars = {
    [81] = 4.09289612,
    [82] = 5.10881490,
    [83] = 6.37689952,
    [84] = 7.95974263,
    [85] = 9.93547022,
    [86] = 12.4800000,
    [87] = 16.2300000,
    [88] = 20.4500000,
    [89] = 26.2800000,
    [90] = 33.3500000,
}

-- 获取等级系数
local function GetRatingScalar(statName, level)
    if statName == "ResilienceRating" then
        return PvpScalars[level] or RatingScalars[level] or 1
    else
        return RatingScalars[level] or 1
    end
end

-- 将属性等级转化为效果百分比（核心方法）
local function GetEffectFromRating(rating, statName, level)
    if type(rating) ~= "number" or not RatingBase[statName] then
        return 0
    end
    
    level = level or UnitLevel("player")
    if level < 34 then
        level = 34
    end
    
    local scalar = RatingBase[statName] * GetRatingScalar(statName, level)
    return rating / scalar
end

-- ==================== 属性名称映射 ====================

local ratingStatMap = {
    ["爆击等级"] = "CritRating",
    ["法术爆击等级"] = "SpellCritRating",
    ["远程爆击等级"] = "RangedCritRating",
    ["命中等级"] = "HitRating",
    ["法术命中等级"] = "SpellHitRating",
    ["远程命中等级"] = "RangedHitRating",
    ["急速等级"] = "HasteRating",
    ["法术急速等级"] = "SpellHasteRating",
    ["远程急速等级"] = "RangedHasteRating",
    ["精准等级"] = "ExpertiseRating",
    ["防御等级"] = "DefenseRating",
    ["躲闪等级"] = "DodgeRating",
    ["招架等级"] = "ParryRating",
    ["格挡等级"] = "BlockRating",
    ["韧性等级"] = "ResilienceRating",
    ["护甲穿透等级"] = "ArmorPenetrationRating",
    ["护甲穿透"] = "ArmorPenetrationRating",
}

-- ==================== 属性转化实现 ====================

local function GetRatingPercent(statName, ratingValue)
    if not statName or not ratingValue then
        return nil
    end
    
    local effect = GetEffectFromRating(ratingValue, statName)
    
    if statName == "DefenseRating" then
        return string.format("%.2f防御", effect)
    end
    
    return effect
end

local function ConvertRatingToPercent(text, colorCode)
    if not text then
        return text
    end
    
    if string.find(text, "%(%+[%d%.]+%%%)") then
        return text
    end
    
    -- 如果没有提供颜色，默认使用金色
    if not colorCode or colorCode == "000000" then
        colorCode = "FFFFD700"
    end
    
    local result = text
    local attributeName, ratingValue
    
    local ratingNames = {
        "爆击等级", "法术爆击等级", "远程爆击等级",
        "命中等级", "法术命中等级", "远程命中等级",
        "急速等级", "法术急速等级", "远程急速等级",
        "精准等级", "防御等级",
        "躲闪等级", "招架等级", "格挡等级",
        "韧性等级", "护甲穿透等级", "护甲穿透"
    }
    
    for _, name in ipairs(ratingNames) do
        local value = string.match(text, name .. "提高(%d+)点")
        if not value then
            value = string.match(text, name .. "提高(%d+)")
        end
        if not value then
            value = string.match(text, "%+(%d+)%s*" .. name)
        end
        if not value then
            value = string.match(text, name .. "%s*%+(%d+)")
        end
        if not value then
            value = string.match(text, name .. ":%s*%+(%d+)")
        end
        if not value then
            value = string.match(text, "提高" .. name .. "(%d+)")
        end
        if not value then
            value = string.match(text, "增加" .. name .. "(%d+)")
        end
        
        if value then
            attributeName = name
            ratingValue = value
            break
        end
    end
    
    if attributeName and ratingValue then
        local statName = ratingStatMap[attributeName]
        if statName then
            local percent = GetRatingPercent(statName, tonumber(ratingValue))
            if percent then
                local percentText
                if type(percent) == "string" then
                    percentText = "|cFF" .. colorCode .. "(" .. percent .. ")|r"
                else
                    percentText = string.format("|cFF" .. colorCode .. "(%.2f%%)|r", percent)
                end
                result = text .. percentText
            end
        end
    end
    
    return result
end

local function UpdateTooltipPercent(tooltip)
    for i = 1, tooltip:NumLines() do
        local line = _G[tooltip:GetName() .. "TextLeft" .. i]
        if line then
            local text = line:GetText()
            if text then
                -- 获取原始文本颜色
                local r, g, b = line:GetTextColor()
                
                -- 判断是否是灰色（r、g、b值接近且较低）
                local isGray = false
                if math.abs(r - g) < 0.1 and math.abs(g - b) < 0.1 and r < 0.7 then
                    isGray = true
                end
                
                -- 如果是灰色，使用灰色；否则使用金色（仅6位RGB）
                local colorCode = isGray and "808080" or "FFD700"
                
                local convertedText = ConvertRatingToPercent(text, colorCode)
                if convertedText ~= text then
                    line:SetText(convertedText)
                end
            end
        end
    end
end


local handler = UpdateTooltipPercent
local enabled = false

local runningHandler = {}

local RunHandler = function(tooltip)
    if enabled and not runningHandler[tooltip] then
        runningHandler[tooltip] = true
        handler(tooltip)
        runningHandler[tooltip] = nil
    end
end

local queuedTooltips = {}

local function HandleUpdate(tooltip)
    if queuedTooltips[tooltip] then
        RunHandler(tooltip)
        queuedTooltips[tooltip] = nil
    end
end

local function QueueUpdate(tooltip)
    queuedTooltips[tooltip] = true
end

local directUpdateTypes = {
    ["GameTooltip"] = true,
    ["CheckButton"] = true,
    ["Button"] = true,
}

local function HandleTooltipSetItem(tooltip)
    local owner = tooltip:GetOwner()
    if (owner and owner.GetObjectType and directUpdateTypes[owner:GetObjectType()]) or debugstack():find("OnUpdate") then
        RunHandler(tooltip)
    elseif owner then
        QueueUpdate(tooltip)
        if not tooltip:GetScript("OnUpdate") then
            tooltip:SetScript("OnUpdate", function(self)
                HandleUpdate(self)
                self:SetScript("OnUpdate", nil)
            end)
        end
    end
end

local tooltips = {
    ["GameTooltip"] = true,
    ["ShoppingTooltip1"] = true,
    ["ShoppingTooltip2"] = true,
    ["ItemRefTooltip"] = true,
    ["ItemRefShoppingTooltip1"] = true,
    ["ItemRefShoppingTooltip2"] = true,
    ["AtlasLootTooltip"] = true,
}

local staticItemSetters = {
    ["SetHyperlink"] = true,
    ["SetItemByID"] = true,
}

local tooltipNeedsRepaint = {}

local initialized = false
local function InitializeHook()
    if initialized then return end
    initialized = true
    
    playerClass = select(2, UnitClass("player"))
    
    local extraHaste = ExtraHasteClasses[playerClass] and 1.3 or 1
    RatingBase["HasteRating"] = 10 / extraHaste
    
    for tooltipName in pairs(tooltips) do
        local tooltip = _G[tooltipName]
        if tooltip then
            tooltip:HookScript("OnTooltipSetItem", HandleTooltipSetItem)
            tooltip:HookScript("OnUpdate", HandleUpdate)

            for functionName in pairs(staticItemSetters) do
                hooksecurefunc(tooltip, functionName, function(self)
                    tooltipNeedsRepaint[self] = true
                end)
                tooltip:HookScript("OnHide", function(self)
                    tooltipNeedsRepaint[self] = nil
                end)
            end

            for i = 1, 60 do
                local fontString = _G[tooltipName .. "TextLeft" .. i]
                if not fontString then
                    local leftName = tooltipName .. "TextLeft" .. i
                    local rightName = tooltipName .. "TextRight" .. i
                    local left = tooltip:CreateFontString(leftName, "ARTWORK", "GameTooltipText")
                    local right = tooltip:CreateFontString(rightName, "ARTWORK", "GameTooltipText")
                    tooltip:AddFontStrings(left, right)
                end
            end
        end
    end
end

local variablesLoaded = false

local eventFrame = CreateFrame("Frame")
eventFrame:RegisterEvent("VARIABLES_LOADED")
eventFrame:SetScript("OnEvent", function(self, event)
    if event == "VARIABLES_LOADED" then
        variablesLoaded = true
        if handler and not initialized then
            InitializeHook()
        end
    end
end)

-- 实时监听开关状态
local checkConfigFrame = CreateFrame("Frame")
checkConfigFrame:SetScript("OnUpdate", function()
    local shouldEnable = false
    if TitanBistooltipAddon and TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.show_rating_percent == true then
        shouldEnable = true
    end
    
    if shouldEnable ~= enabled then
        enabled = shouldEnable
    end
end)

-- 自动比较装备：实时同步，永不失效
local autoCompareFrame = CreateFrame("Frame")
autoCompareFrame:RegisterEvent("VARIABLES_LOADED")
autoCompareFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
autoCompareFrame:RegisterEvent("UPDATE_MACROS")
autoCompareFrame:SetScript("OnEvent", function()
    C_Timer.After(1, function()
        if TitanBistooltipAddon and TitanBistooltipAddon.db and TitanBistooltipAddon.db.global then
            if TitanBistooltipAddon.db.global.auto_compare_items then
                ConsoleExec("set alwaysCompareItems 1")
            else
                ConsoleExec("set alwaysCompareItems 0")
            end
        end
    end)
end)
