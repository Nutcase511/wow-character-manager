-- TitanBistooltip_PawnIntegration.lua
-- 此功能快跑兄弟正在进行中，未实装.

-- Pawn集成模块
local function TitanBistooltip_AddPawnScales()
    if not PawnAddPluginScale then return end
    
    -- WoW Classic职业ID映射
    local classIDs = {
        ["Warrior"] = 1,
        ["Paladin"] = 2,
        ["Hunter"] = 3,
        ["Rogue"] = 4,
        ["Priest"] = 5,
        ["Death knight"] = 6,
        ["Shaman"] = 7,
        ["Mage"] = 8,
        ["Warlock"] = 9,
        ["Druid"] = 11
    }
    
    -- 专精ID映射（每个职业的专精顺序）
    local specIDs = {
        -- Death knight
        {class = "Death knight", specs = {1, 2, 3, 4}}, -- Blood tank, Blood dps, Frost, Unholy
        -- Druid
        {class = "Druid", specs = {1, 2, 3, 4}}, -- Balance, Feral tank, Feral dps, Restoration
        -- Hunter
        {class = "Hunter", specs = {1, 2, 3}}, -- Beast mastery, Marksmanship, Survival
        -- Mage
        {class = "Mage", specs = {1, 2, 3, 4}}, -- Arcane, Fire, Fire FFB, Frost
        -- Paladin
        {class = "Paladin", specs = {1, 2, 3}}, -- Holy, Protection, Retribution
        -- Priest
        {class = "Priest", specs = {1, 2, 3}}, -- Discipline, Holy, Shadow
        -- Rogue
        {class = "Rogue", specs = {1, 2, 3}}, -- Assassination, Combat, Subtlety
        -- Shaman
        {class = "Shaman", specs = {1, 2, 3}}, -- Elemental, Enhancement, Restoration
        -- Warrior
        {class = "Warrior", specs = {1, 2, 3}}, -- Arms, Fury, Protection
        -- Warlock
        {class = "Warlock", specs = {1, 2, 3}} -- Affliction, Demonology, Destruction
    }
    
    -- 默认属性权重（可以后续根据BIS数据动态计算）
    local defaultWeights = {
        -- 物理DPS
        {class = "Warrior", specs = {["Arms"] = {Strength=2.5, Stamina=1.0, CritRating=1.8, HasteRating=1.5, MasteryRating=1.6, Versatility=1.3},
                                      ["Fury"] = {Strength=2.5, Stamina=1.0, CritRating=1.8, HasteRating=1.6, MasteryRating=1.4, Versatility=1.3},
                                      ["Protection"] = {Strength=2.0, Stamina=1.5, CritRating=1.2, HasteRating=1.3, MasteryRating=1.8, Versatility=1.4}}},
        -- 圣骑士
        {class = "Paladin", specs = {["Holy"] = {Intellect=2.5, Stamina=1.0, CritRating=1.5, HasteRating=1.6, MasteryRating=1.4, Versatility=1.3},
                                     ["Protection"] = {Strength=2.0, Stamina=1.5, CritRating=1.2, HasteRating=1.3, MasteryRating=1.8, Versatility=1.4},
                                     ["Retribution"] = {Strength=2.5, Stamina=1.0, CritRating=1.8, HasteRating=1.5, MasteryRating=1.6, Versatility=1.3}}},
        -- 其他职业...
    }
    
    -- 检查TitanBistooltip_Titan_classes是否存在
    local classes = _G.TitanBistooltip_Titan_classes or TitanBistooltip_Titan_classes
    local phases = _G.TitanBistooltip_Titan_phases or TitanBistooltip_Titan_phases or {"PR", "P1", "P2", "P3", "P4"}
    
    if not classes then return end
    
    -- 遍历所有职业
    for classIndex, classData in ipairs(classes) do
        local className = classData.name
        local classID = classIDs[className]
        
        if classID and classData.specs then
            -- 遍历所有专精
            for specIndex, specName in ipairs(classData.specs) do
                -- 为每个阶段添加评分模板
                for phaseIndex, phaseName in ipairs(phases) do
                    -- 构建评分名称
                    local scaleName = string.format("%s - %s - %s", className, specName, phaseName)
                    local displayName = string.format("%s %s (%s)", className, specName, phaseName)
                    
                    -- 使用通用权重（实际应该根据BIS数据计算）
                    local weights = {
                        Strength = 2.0,
                        Agility = 2.0,
                        Intellect = 2.0,
                        Stamina = 1.0,
                        CriticalStrikeRating = 1.5,
                        HasteRating = 1.4,
                        MasteryRating = 1.4,
                        Versatility = 1.2
                    }
                    
                    -- 添加评分模板
                    PawnAddPluginScale(
                        "TitanBistooltip",
                        scaleName,
                        displayName,
                        "00bfff",
                        weights,
                        100,
                        nil
                    )
                end
            end
        end
    end
end

-- 初始化函数
local function TitanBistooltip_InitializePawnIntegration()
    -- 检查Pawn是否加载
    if not Pawn or not PawnAddPluginScaleProvider then
        return false
    end
    
    -- 注册插件提供者
    PawnAddPluginScaleProvider("TitanBistooltip", "TitanBisTooltip", function()
        TitanBistooltip_AddPawnScales()
    end)
    
    return true
end

-- 监听事件，在Pawn加载后初始化
local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, event, addonName)
    if addonName == "Pawn" then
        TitanBistooltip_InitializePawnIntegration()
        frame:UnregisterEvent("ADDON_LOADED")
    end
end)

-- 尝试立即初始化（如果Pawn已经加载）
TitanBistooltip_InitializePawnIntegration()