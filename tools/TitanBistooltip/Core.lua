TitanBistooltipAddon = LibStub("AceAddon-3.0"):NewAddon("TitanBistooltip")

-- 插件版本信息
TitanBistooltipAddon.Version = "2.21" -- 版本号
TitanBistooltipAddon.AddonNameAndVersion = "TitanBistooltip v" .. TitanBistooltipAddon.Version

-- 确保版本信息在全局可访问
_G["TitanBistooltipAddon"] = TitanBistooltipAddon

-- 全局函数用于按键绑定
function TitanBistooltipToggle()
    if TitanBistooltipAddon and TitanBistooltipAddon.ToggleBisListFrame then
        TitanBistooltipAddon:ToggleBisListFrame()
    end
end

-- 全局函数用于按键绑定 - 毕业配装面板
function TitanBistooltipToggleMaxed()
    if TitanBistooltipAddon and TitanBistooltipAddon.showMaxedFrame then
        TitanBistooltipAddon:showMaxedFrame()
    end
end

-- 防抖功能
local tooltip_timer = nil
local function debounceTooltip(callback, delay)  
    if tooltip_timer then
        tooltip_timer:Cancel()
    end
    tooltip_timer = C_Timer.NewTimer(delay, callback)
end

-- 装备扫描优化
local last_scan_time = 0
local scan_interval = 5 -- 5秒

-- 角色列表框架
local characterListFrame = nil

-- 角色装备面板框架
local characterEquipmentFrame = nil

-- 显示角色列表
function TitanBistooltipAddon:showCharacterList()
    -- 销毁旧的角色列表框架
    if characterListFrame then
        characterListFrame:Hide()
        characterListFrame = nil
    end
    
    -- 创建新的角色列表框架
    characterListFrame = CreateFrame("Frame", nil, UIParent, "UIDropDownMenuTemplate")
    
    -- 获取账号下所有角色
    local characters = {}
    
    -- 使用默认的API获取角色信息
    local numCharacters
    if C_CharacterCache and C_CharacterCache.GetNumCharacters then
        numCharacters = C_CharacterCache.GetNumCharacters()
        for i = 1, numCharacters do
            local charInfo = C_CharacterCache.GetCharacterInfo(i)
            if charInfo and charInfo.name and charInfo.classFileName then
                table.insert(characters, {
                    name = charInfo.name,
                    classFileName = charInfo.classFileName,
                    isActive = charInfo.isActive
                })
            end
        end
    else
        numCharacters = GetNumCharacters()
        for i = 1, numCharacters do
            local name, _, _, _, _, classFileName, _, _, _, _, _, _, _, _, _, _, _, _, isActive = GetCharacterInfo(i)
            if name and classFileName then
                table.insert(characters, {
                    name = name,
                    classFileName = classFileName,
                    isActive = isActive
                })
            end
        end
    end
    
    -- 构建下拉菜单
    local menuList = {}
    
    for _, char in ipairs(characters) do
        local classColor = RAID_CLASS_COLORS[char.classFileName]
        if classColor then
            local colorCode = "|cff" .. string.format("%02x%02x%02x", classColor.r * 255, classColor.g * 255, classColor.b * 255)
            table.insert(menuList, {
                text = colorCode .. char.name .. "|r",
                func = function()
                    TitanBistooltipAddon:showCharacterEquipment(char.name, char.classFileName)
                end,
                checked = char.isActive
            })
        else
            table.insert(menuList, {
                text = char.name,
                func = function()
                    TitanBistooltipAddon:showCharacterEquipment(char.name, char.classFileName)
                end,
                checked = char.isActive
            })
        end
    end
    
    -- 如果没有角色数据，添加一个提示项
    if #menuList == 0 then
        table.insert(menuList, {
            text = "|cffff0000没有找到角色数据|r",
            disabled = true
        })
    end
    
    -- 显示下拉菜单
    EasyMenu(menuList, characterListFrame, "cursor", 0, 0, "MENU")
end

-- 显示角色装备面板
function TitanBistooltipAddon:showCharacterEquipment(characterName, classFileName)
    -- 销毁旧的角色装备面板框架
    if characterEquipmentFrame then
        characterEquipmentFrame:Hide()
        characterEquipmentFrame = nil
    end
    
    -- 创建新的角色装备面板框架
    characterEquipmentFrame = AceGUI:Create("Frame")
    characterEquipmentFrame:SetWidth(435)
    characterEquipmentFrame:SetHeight(500)
    characterEquipmentFrame.frame:SetResizeBounds(435, 300, 435, 880)
    
    -- 设置面板标题
    local classColor = RAID_CLASS_COLORS[classFileName]
    local colorCode = "|cff" .. string.format("%02x%02x%02x", classColor.r * 255, classColor.g * 255, classColor.b * 255)
    characterEquipmentFrame:SetTitle(colorCode .. characterName .. "|r 的装备")
    characterEquipmentFrame:SetLayout("List")
    
    -- 设置关闭回调
    characterEquipmentFrame:SetCallback("OnClose", function(widget)
        widget.frame:Hide()
    end)
    
    -- 复用或创建滚动框架
    if not controlRefs.scrollFrame then
        controlRefs.scrollFrame = AceGUI:Create("ScrollFrame")
        controlRefs.scrollFrame:SetLayout("Table")
        controlRefs.scrollFrame:SetUserData("table", {
            columns = {
                { width = 130 },  -- 部位名称
                { width = 44 },   -- 装备图标
                { width = 120 },  -- 装备名称
                { width = 10 },   -- 间隔
                { width = 120 },  -- 附魔名称
                { width = 44 },   -- 附魔图标
                { width = 10 },   -- 间隔
                { width = 44 },   -- 宝石1图标
                { width = 44 },   -- 宝石2图标
                { width = 44 },   -- 宝石3图标
                { width = 44 }    -- 宝石4图标
            },
            space = 1,
            align = "middle"
        })
        controlRefs.scrollFrame:SetFullWidth(true)
        controlRefs.scrollFrame:SetFullHeight(true)
        controlRefs.scrollFrame:SetAutoAdjustHeight(false)
        characterEquipmentFrame:AddChild(controlRefs.scrollFrame)
    else
        controlRefs.scrollFrame:ReleaseChildren()
    end
    
    -- 使用复用的滚动框架
    local scrollFrame = controlRefs.scrollFrame
    scrollFrame:SetHeight(400)
    
    -- 绘制表头
    local headerLabel = AceGUI:Create("Label")
    headerLabel:SetText("部位")
    headerLabel:SetColor(0.6, 0.6, 0.6)
    scrollFrame:AddChild(headerLabel)
    scrollFrame:AddChild(AceGUI:Create("Label"))
    local itemLabel = AceGUI:Create("Label")
    itemLabel:SetText("装备")
    itemLabel:SetColor(0.6, 0.6, 0.6)
    scrollFrame:AddChild(itemLabel)
    for i = 1, 5 do
        scrollFrame:AddChild(AceGUI:Create("Label"))
    end
    
    -- 这里需要添加获取角色装备的代码
    -- 由于WoW API限制，无法直接获取其他角色的装备
    -- 这里使用示例数据
    local exampleSlots = {
        { slot_name = "Head", items = { 12345 } },
        { slot_name = "Neck", items = { 12346 } },
        { slot_name = "Shoulder", items = { 12347 } },
        { slot_name = "Back", items = { 12348 } },
        { slot_name = "Chest", items = { 12349 } },
        { slot_name = "Wrist", items = { 12350 } },
        { slot_name = "Hands", items = { 12351 } },
        { slot_name = "Waist", items = { 12352 } },
        { slot_name = "Legs", items = { 12353 } },
        { slot_name = "Feet", items = { 12354 } },
        { slot_name = "Finger", items = { 12355 } },
        { slot_name = "Finger", items = { 12356 } },
        { slot_name = "Trinket", items = { 12357 } },
        { slot_name = "Trinket", items = { 12358 } },
        { slot_name = "Weapon", items = { 12359 } },
        { slot_name = "Off hand", items = { 12360 } }
    }
    
    -- 绘制装备槽位
    for _, slot in ipairs(exampleSlots) do
        local slotLabel = AceGUI:Create("Label")
        slotLabel:SetText(slot.slot_name)
        scrollFrame:AddChild(slotLabel)
        scrollFrame:AddChild(AceGUI:Create("Label"))
        
        for _, itemId in ipairs(slot.items) do
            local itemFrame = AceGUI:Create("Icon")
            itemFrame:SetImageSize(40, 40)
            
            -- 设置物品图标
            local itemTexture
            
            -- 优先从缓存获取
            if itemInfoCache[itemId] and itemInfoCache[itemId].texture then
                itemTexture = itemInfoCache[itemId].texture
            else
                -- 从API获取
                if C_Item and C_Item.GetItemInfo then
                    local itemInfo = C_Item.GetItemInfo(itemId)
                    if itemInfo then
                        itemTexture = itemInfo.iconFileID
                    end
                else
                    local itemName, itemLink, itemQuality, itemLevel, itemMinLevel, itemType, itemSubType, itemStackCount, itemEquipLoc, texture = GetItemInfo(itemId)
                    itemTexture = texture
                end
                
                -- 缓存物品信息
                if not itemInfoCache[itemId] then
                    itemInfoCache[itemId] = {}
                end
                itemInfoCache[itemId].texture = itemTexture
            end
            
            if itemTexture then
                itemFrame:SetImage(itemTexture)
            else
                itemFrame:SetImage("Interface/Icons/INV_Misc_QuestionMark")
            end
            
            -- 设置点击事件
            itemFrame:SetCallback("OnClick", function(widget, event, button)
                if button == "LeftButton" and itemLink then
                    SetItemRef(itemLink, itemLink, "LeftButton")
                end
            end)
            
            -- 设置鼠标悬停事件
            itemFrame:SetCallback("OnEnter", function(widget)
                debounceTooltip(function()
                    GameTooltip:SetOwner(widget.frame)
                    
                    -- 获取面板位置，自动调整提示框方向
                    local frame = widget:GetParent()
                    while frame and not frame:IsForbidden() do
                        if frame.GetRight then
                            break
                        end
                        frame = frame:GetParent()
                    end
                    
                    local screenWidth = GetScreenWidth()
                    local frameRight = frame and frame:GetRight() or 0
                    local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                    
                    if smartPosition and frameRight > screenWidth / 2 then
                        -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧，增加偏移距离避免覆盖
                        GameTooltip:SetPoint("TOPLEFT", widget.frame, "TOPLEFT", -300, -13)
                    else
                        -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧，增加偏移距离避免覆盖
                        GameTooltip:SetPoint("TOPRIGHT", widget.frame, "TOPRIGHT", 300, -13)
                    end
                    
                    if itemLink then
                        GameTooltip:SetHyperlink(itemLink)
                    else
                        GameTooltip:SetText("物品信息加载中...")
                    end
                end, 0.05) -- 50ms延迟
            end)
            
            itemFrame:SetCallback("OnLeave", function(widget)
                if tooltip_timer then
                    tooltip_timer:Cancel()
                    tooltip_timer = nil
                end
                GameTooltip:Hide()
            end)
            
            scrollFrame:AddChild(itemFrame)
        end
        
        -- 填充剩余空格
        for i = #slot.items + 1, 6 do
            scrollFrame:AddChild(AceGUI:Create("Label"))
        end
    end
    
    -- 显示面板
    characterEquipmentFrame.frame:Show()
end
--local AceAddon =

TitanBistooltip_char_equipment = {}

-- 排名缓存，用于存储装备排名信息
local rank_cache = {}

-- 保存控件引用，用于复用
local controlRefs = {
    scrollFrame = nil
}

-- 装备信息缓存
local itemInfoCache = {}

-- 阶段间装备继承功能：当当前阶段装备有空缺时，自动从前一阶段填充
local function inheritEquipmentFromPreviousPhase()
    local phases = TitanBistooltip_phases
    for class_name, class_data in pairs(TitanBistooltip_bislists) do
        for spec_name, spec_data in pairs(class_data) do
            -- 按阶段顺序处理（PR → P1 → P2 → P3 → ...）
            for phase_index = 2, #phases do
                local current_phase = phases[phase_index]
                local previous_phase = phases[phase_index - 1]
                
                -- 检查前一阶段是否存在该职业专精的数据
                if spec_data[previous_phase] and spec_data[current_phase] then
                    for slot_index, current_slot in ipairs(spec_data[current_phase]) do
                        local previous_slot = nil
                        -- 找到前一阶段相同部位的slot
                        for _, prev_s in ipairs(spec_data[previous_phase]) do
                            if prev_s.slot_name == current_slot.slot_name then
                                previous_slot = prev_s
                                break
                            end
                        end
                        
                        if previous_slot then
                            -- 使用哈希表存储当前槽位已有的装备ID，避免内层循环检查重复
                            local existing_items = {}
                            for i = 1, 6 do
                                if current_slot[i] and current_slot[i] ~= -1 then
                                    existing_items[current_slot[i]] = true
                                end
                            end
                            
                            -- 填充当前阶段的-1空缺位置
                            local fill_index = 1
                            for i = 1, 6 do
                                if current_slot[i] == -1 or current_slot[i] == nil then
                                    -- 从前一阶段找可用的装备
                                    while fill_index <= 6 do
                                        local prev_item = previous_slot[fill_index]
                                        if prev_item and prev_item ~= -1 and not existing_items[prev_item] then
                                            -- 装备不存在，添加到当前槽位
                                            current_slot[i] = prev_item
                                            existing_items[prev_item] = true
                                            fill_index = fill_index + 1
                                            break
                                        end
                                        fill_index = fill_index + 1
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
end

function TitanBistooltip_ScanEquipment()
    -- 减少扫描频率，避免频繁扫描导致卡顿
    local current_time = GetTime()
    if current_time - last_scan_time < scan_interval then
        -- 未到扫描时间，直接返回
        return
    end
    
    -- 更新扫描时间
    last_scan_time = current_time
    
    -- 使用pcall包装，避免扫描过程中出错
    local success, result = pcall(function()
        local collection = {}
        
        -- 扫描装备栏
        if C_PlayerInfo and C_PlayerInfo.GetInventoryItemID then
            -- 正式服API使用1-19作为装备栏位
            for i=1,19 do
                local itemID = C_PlayerInfo.GetInventoryItemID("player", i)
                if itemID ~= nil then
                    collection[itemID] = 2
                end
            end
        elseif GetInventoryItemID then
            -- 旧API使用0-18
            for i=0,18 do
                local itemID = GetInventoryItemID("player", i)
                if itemID ~= nil then
                    collection[itemID] = 2
                end
            end
        end
        
        -- 扫描背包
        if C_Container and C_Container.GetContainerNumSlots and C_Container.GetContainerItemID then
            -- 正式服API遍历所有背包
            for bag = 0, 4 do -- 0-4是背包栏位
                local numSlots = C_Container.GetContainerNumSlots(bag)
                for slot = 1, numSlots do
                    local itemID = C_Container.GetContainerItemID(bag, slot)
                    if itemID ~= nil then
                        -- 只有在装备栏中不存在时才标记为1（背包）
                        if not collection[itemID] then
                            collection[itemID] = 1
                        end
                    end
                end
            end
        elseif GetContainerNumSlots and GetContainerItemID then
            -- 使用旧 API
            for bag = 0, 4 do -- 0-4是背包栏位
                local numSlots = GetContainerNumSlots(bag)
                for slot = 1, numSlots do
                    local itemID = GetContainerItemID(bag, slot)
                    if itemID ~= nil then
                        -- 只有在装备栏中不存在时才标记为1（背包）
                        if not collection[itemID] then
                            collection[itemID] = 1
                        end
                    end
                end
            end
        end
        
        return collection
    end)
    
    -- 如果扫描成功，更新装备数据
    if success and result then
        TitanBistooltip_char_equipment = result
        -- 清除 TitanBistooltip_equipmentCache 缓存，确保下次打开 BIS 面板时重新检查装备状态
        if TitanBistooltip_equipmentCache then
            TitanBistooltip_equipmentCache = {}
        end
    else
        -- 扫描失败，记录错误
        DEFAULT_CHAT_FRAME:AddMessage("|cffff0000装备扫描失败: " .. tostring(result) .. "|r")
    end
end

-- 复制文本到剪贴板的公共函数
function TitanBistooltipAddon:CopyTextToClipboard(text)
    if text and text ~= "" then
        -- 使用全局永久 EditBox 进行复制
        if not _G.TitanBistooltipCopyEditBox then
            _G.TitanBistooltipCopyEditBox = CreateFrame("EditBox", "TitanBistooltipCopyEditBox", UIParent, "InputBoxTemplate")
            _G.TitanBistooltipCopyEditBox:SetSize(200, 20)
            _G.TitanBistooltipCopyEditBox:SetMultiLine(false)
            _G.TitanBistooltipCopyEditBox:SetAutoFocus(false)
            _G.TitanBistooltipCopyEditBox:ClearAllPoints()
            _G.TitanBistooltipCopyEditBox:SetPoint("TOPLEFT", UIParent, "TOPLEFT", -1000, -1000) -- 放到屏幕外
            _G.TitanBistooltipCopyEditBox:Hide()
        end
        
        local editBox = _G.TitanBistooltipCopyEditBox
        
        -- 执行复制操作
        local success, err = pcall(function()
            editBox:Show()
            editBox:SetText(text)
            editBox:HighlightText(0, -1) -- 高亮整个文本
            
            -- 检查是否有 CopyText 方法
            if editBox.CopyText then
                editBox:CopyText()
            else
                -- WLK 版本不支持 CopyText，尝试使用替代方法
                -- 首先尝试直接向聊天框输入
                local chatFrame = ChatEdit_GetActiveWindow()
                if chatFrame then
                    chatFrame:Insert(text)
                    success = true
                else
                    -- 没有聊天框激活，显示提示
                    DEFAULT_CHAT_FRAME:AddMessage("|cffffff00请打开聊天窗口后再右键点击复制|r")
                    success = false
                end
            end
            
            editBox:Hide()
        end)
        
        if not success and err then
            DEFAULT_CHAT_FRAME:AddMessage("|cffff0000复制到剪贴板失败: " .. tostring(err) .. "|r")
        end
        
        return success
    end
    return false
end

-- 全局引用BIS面板框架
local main_frame_ref = nil

-- 设置main_frame引用
function TitanBistooltipAddon:setMainFrameRef(frame)
    main_frame_ref = frame
end

local function createEquipmentWatcher()
    local frame = CreateFrame("Frame")
    frame:Hide()

    frame:SetScript("OnEvent", frame.Show)
    frame:RegisterEvent("BAG_UPDATE")
    frame:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")

    local flag = false

    frame:SetScript("OnUpdate", function(self)
        self:Hide()
        if flag == false then
            flag = true
            TitanBistooltip_ScanEquipment()
            flag = false
        end
    end)
    
    -- 立即执行一次装备扫描
    TitanBistooltip_ScanEquipment()
end

local function getPlayerClassAndSpec()
    local englishClass, classIndex
    if C_PlayerInfo and C_PlayerInfo.GetClass then
        local classInfo
        -- 尝试使用 PlayerLocation 对象（现代API）
        if PlayerLocation and PlayerLocation.CreateFromUnit then
            local playerLocation = PlayerLocation:CreateFromUnit("player")
            classInfo = C_PlayerInfo.GetClass(playerLocation)
        end
        -- 如果现代API失败，尝试使用字符串 "player"（旧API）
        if not classInfo then
            classInfo = C_PlayerInfo.GetClass("player")
        end
        if classInfo then
            englishClass = classInfo.classFile
            classIndex = classInfo.classID
        end
    else
        local _, englishClass_temp, classIndex_temp = UnitClass("player")
        englishClass = englishClass_temp
        classIndex = classIndex_temp
    end
    local specIndex = nil
    local specName = nil
    local specID = nil
    
    -- 检查GetSpecialization函数是否存在
    if C_PlayerInfo and C_PlayerInfo.GetSpecialization then
        local specInfo
        -- 尝试使用 PlayerLocation 对象（现代API）
        if PlayerLocation and PlayerLocation.CreateFromUnit then
            local playerLocation = PlayerLocation:CreateFromUnit("player")
            specInfo = C_PlayerInfo.GetSpecialization(playerLocation)
        end
        -- 如果现代API失败，尝试使用字符串 "player"（旧API）
        if not specInfo then
            specInfo = C_PlayerInfo.GetSpecialization("player")
        end
        if specInfo then
            specID = specInfo.specID
            specName = specInfo.name
        end
    elseif GetSpecialization then
        specIndex = GetSpecialization()
        if specIndex and GetSpecializationInfo then
            specID, specName = GetSpecializationInfo(specIndex)
        end
    end
    
    -- 映射职业名称到插件内部使用的格式
    local classMap = {
        ["DEATHKNIGHT"] = "Death knight",
        ["DRUID"] = "Druid",
        ["HUNTER"] = "Hunter",
        ["MAGE"] = "Mage",
        ["PALADIN"] = "Paladin",
        ["PRIEST"] = "Priest",
        ["ROGUE"] = "Rogue",
        ["SHAMAN"] = "Shaman",
        ["WARLOCK"] = "Warlock",
        ["WARRIOR"] = "Warrior"
    }
    
    local mappedClassName = classMap[englishClass]
    
    -- 映射天赋名称到插件内部使用的格式
    local specMap = {
        ["Death knight"] = {
            ["Blood"] = "Blood tank",
            ["Frost"] = "Frost",
            ["Unholy"] = "Unholy"
        },
        ["Druid"] = {
            ["Balance"] = "Balance",
            ["Feral Combat"] = "Feral dps",
            ["Feral"] = "Feral dps", -- 添加对不同版本天赋名称的支持
            ["Guardian"] = "Feral tank",
            ["Restoration"] = "Restoration"
        },
        ["Hunter"] = {
            ["Beast Mastery"] = "Beast mastery",
            ["Marksmanship"] = "Marksmanship",
            ["Survival"] = "Survival"
        },
        ["Mage"] = {
            ["Arcane"] = "Arcane",
            ["Fire"] = "Fire",
            ["Frost"] = "Frost"
        },
        ["Paladin"] = {
            ["Holy"] = "Holy",
            ["Protection"] = "Protection",
            ["Retribution"] = "Retribution"
        },
        ["Priest"] = {
            ["Discipline"] = "Discipline",
            ["Holy"] = "Holy",
            ["Shadow"] = "Shadow"
        },
        ["Rogue"] = {
            ["Assassination"] = "Assassination",
            ["Combat"] = "Combat",
            ["Subtlety"] = "Subtlety"
        },
        ["Shaman"] = {
            ["Elemental"] = "Elemental",
            ["Enhancement"] = "Enhancement",
            ["Restoration"] = "Restoration"
        },
        ["Warlock"] = {
            ["Affliction"] = "Affliction",
            ["Demonology"] = "Demonology",
            ["Destruction"] = "Destruction"
        },
        ["Warrior"] = {
            ["Arms"] = "Arms",
            ["Fury"] = "Fury",
            ["Protection"] = "Protection"
        }
    }
    
    local mappedSpecName = specMap[mappedClassName] and specMap[mappedClassName][specName]
    
    -- 如果没有找到映射，尝试一些常见的变体
    if not mappedSpecName and mappedClassName == "Druid" then
        if specName == "Feral" then
            mappedSpecName = "Feral dps"
        elseif specName == "Guardian" then
            mappedSpecName = "Feral tank"
        end
    end
    
    return mappedClassName, mappedSpecName
end

-- 确保过滤器配置正确
local function ensureFilterConfig(className, specName)
    -- 确保highlight_specs表存在
    if not TitanBistooltipAddon.db.global.highlight_specs then
        TitanBistooltipAddon.db.global.highlight_specs = {}
    end
    
    -- 确保过滤器配置正确
    if not TitanBistooltipAddon.db.global.filter_specs[className] then
        TitanBistooltipAddon.db.global.filter_specs[className] = {}
    end
    
    -- 确保当前天赋的过滤器为false（显示）
    if specName and TitanBistooltipAddon.db.global.filter_specs[className][specName] == nil then
        TitanBistooltipAddon.db.global.filter_specs[className][specName] = false
    end
end

-- 更新职业和天赋索引
local function updateClassAndSpecIndexes(className, specName)
    -- 更新配置中的职业、天赋和阶段索引，用于BIS装备面板
    local classIndex = TitanBistooltip_classes_indexes[className]
    if classIndex then
        -- 只有当class_index未设置时才自动设置，这样用户手动修改后就不会被重置
        if not TitanBistooltipAddon.db.global.class_index then
            TitanBistooltipAddon.db.global.class_index = classIndex
        end
        
        -- 查找对应的天赋索引
        local foundSpecIndex = nil
        if specName and TitanBistooltip_classes and TitanBistooltip_classes[classIndex] then
            for specIndex, spec in ipairs(TitanBistooltip_classes[classIndex].specs) do
                if spec == specName then
                    foundSpecIndex = specIndex
                    break
                end
            end
        end
        
        -- 如果找到了对应的天赋索引，使用它
        if foundSpecIndex then
            TitanBistooltipAddon.db.global.spec_index = foundSpecIndex
        else
            -- 如果没有找到对应的天赋索引，尝试根据GetSpecialization返回的索引来设置
            local specIndex
            if C_PlayerInfo and C_PlayerInfo.GetSpecialization then
                local specInfo = C_PlayerInfo.GetSpecialization("player")
                if specInfo then
                    specIndex = specInfo.specIndex
                end
            elseif GetSpecialization then
                specIndex = GetSpecialization()
            end
            if specIndex and TitanBistooltip_classes and TitanBistooltip_classes[classIndex] then
                -- 根据specIndex设置一个合理的默认值
                if className == "Druid" then
                    -- 对于德鲁伊，1=平衡（鸟德），2=熊德（野性坦克），3=猫德（野性输出），4=恢复（奶德）
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- 平衡
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- 野性坦克
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- 野性输出
                    elseif specIndex == 4 then
                        TitanBistooltipAddon.db.global.spec_index = 4 -- 恢复
                    end
                elseif className == "Death knight" then
                    -- 对于死亡骑士，1=鲜血，2=冰霜，3=邪恶
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Blood tank
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Frost
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Unholy
                    end
                elseif className == "Hunter" then
                    -- 对于猎人，1=野兽控制，2=射击，3=生存
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Beast mastery
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Marksmanship
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Survival
                    end
                elseif className == "Mage" then
                    -- 对于法师，1=奥术，2=火焰，3=冰霜
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Arcane
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Fire
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Frost
                    end
                elseif className == "Paladin" then
                    -- 对于圣骑士，1=神圣，2=防护，3=惩戒
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Holy
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Protection
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Retribution
                    end
                elseif className == "Priest" then
                    -- 对于牧师，1=戒律，2=神圣，3=暗影
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Discipline
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Holy
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Shadow
                    end
                elseif className == "Rogue" then
                    -- 对于盗贼，1=刺杀，2=战斗，3=敏锐
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Assassination
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Combat
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Subtlety
                    end
                elseif className == "Shaman" then
                    -- 对于萨满，1=元素，2=增强，3=恢复
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Elemental
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Enhancement
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Restoration
                    end
                elseif className == "Warlock" then
                    -- 对于术士，1=痛苦，2=恶魔学识，3=毁灭
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Affliction
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Demonology
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Destruction
                    end
                elseif className == "Warrior" then
                    -- 对于战士，1=武器，2=狂怒，3=防护
                    if specIndex == 1 then
                        TitanBistooltipAddon.db.global.spec_index = 1 -- Arms
                    elseif specIndex == 2 then
                        TitanBistooltipAddon.db.global.spec_index = 2 -- Fury
                    elseif specIndex == 3 then
                        TitanBistooltipAddon.db.global.spec_index = 3 -- Protection
                    end
                end
            end
        end
    end
    
    -- 保持当前阶段设置，或者使用配置中的默认值
    if not TitanBistooltipAddon.db.global.phase_index then
        -- 从设置中读取默认阶段
        local defaultPhase = TitanBistooltipAddon.db.global.default_phase or "P3"
        -- 确保TitanBistooltip_phases被正确初始化
        local phases = TitanBistooltip_phases or { "PR" , "P1" , "P2" , "P3" , "P4" , "P5" , "P6" , "P7" , "P8" , "P9" , "P10" , "P11" }
        -- 找到默认阶段在阶段列表中的索引
        local phaseIndex = 1
        for i, phase in ipairs(phases) do
            if phase == defaultPhase then
                phaseIndex = i
                break
            end
        end
        TitanBistooltipAddon.db.global.phase_index = phaseIndex
    end
end

-- 自动识别当前角色职业和天赋
local function autoDetectClassAndSpec()
    local className, mappedSpecName = getPlayerClassAndSpec()
    
    if className then
        -- 确保过滤器配置正确
        ensureFilterConfig(className, mappedSpecName)
        
        -- 更新职业和天赋索引
        updateClassAndSpecIndexes(className, mappedSpecName)
        
        -- 重新加载数据，确保全局变量和界面更新
        if TitanBistooltipAddon.reloadData then
            TitanBistooltipAddon:reloadData()
        end
    end
end

function TitanBistooltipAddon:OnInitialize()
    createEquipmentWatcher()
    TitanBistooltipAddon.AceAddonName = "TitanBistooltip"

    
    TitanBistooltipAddon:initConfig()
    TitanBistooltipAddon:addMapIcon()
    TitanBistooltipAddon:initBislists()
    
    -- 预处理阶段间装备继承
    inheritEquipmentFromPreviousPhase()
    
    -- 全局装备ID到信息的映射表，用于快速查找
    TitanBistooltip_item_mapping = {}
    
    -- 更新TitanBistooltip_Titan_items缓存和装备映射表
    local function updateItemsCache()
        -- 创建一个临时表，用于存储所有装备的信息
        local temp_items = {}
        local temp_mapping = {} -- 装备ID到信息的直接映射
        
        -- 分批次处理装备数据，避免一次性处理过多数据导致卡顿
        local class_list = {}
        for class_name, _ in pairs(TitanBistooltip_bislists) do
            table.insert(class_list, class_name)
        end
        
        local batch_size = 2 -- 每批次处理2个职业
        local current_index = 1
        local total_classes = #class_list
        
        local function processBatch()
            if current_index > total_classes then
                -- 所有批次处理完成，转换为TitanBistooltip_Titan_items的格式
                for itemId, item_data in pairs(temp_items) do
                    -- 按职业分组，同一职业的所有专精都放在一起
                    local class_map = {}
                    for _, entry in ipairs(item_data) do
                        local class_name = entry.class_name
                        local spec_name = entry.spec_name
                        local slot_name = entry.slot_name
                        
                        -- 检查职业是否已经存在
                        if not class_map[class_name] then
                            class_map[class_name] = {}
                        end
                        
                        -- 检查专精是否已经存在
                        if not class_map[class_name][spec_name] then
                            class_map[class_name][spec_name] = {
                                class_name = class_name,
                                spec_name = spec_name,
                                slots = {}
                            }
                        end
                        
                        -- 检查槽位是否已经存在
                        local slot_exists = false
                        for _, existing_slot in ipairs(class_map[class_name][spec_name].slots) do
                            if existing_slot.name == slot_name then
                                slot_exists = true
                                break
                            end
                        end
                        
                        if not slot_exists then
                            -- 添加槽位
                            table.insert(class_map[class_name][spec_name].slots, {
                                name = slot_name,
                                ranks = "- / - / -" -- 占位符，实际排名会动态计算
                            })
                        end
                    end
                    
                    -- 更新TitanBistooltip_Titan_items
                    TitanBistooltip_Titan_items[itemId] = {}
                    
                    -- 添加缓存时间戳和访问时间
                    local current_time = GetTime()
                    TitanBistooltip_Titan_items[itemId]._cache_time = current_time
                    TitanBistooltip_Titan_items[itemId]._last_access_time = current_time
                    
                    -- 转换为TitanBistooltip_Titan_items的格式
                    for _, specs in pairs(class_map) do
                        for _, item_info in pairs(specs) do
                            table.insert(TitanBistooltip_Titan_items[itemId], item_info)
                        end
                    end
                end
                
                -- 更新装备映射表
                TitanBistooltip_item_mapping = temp_mapping
                
                -- 更新缓存时间和版本信息
                TitanBistooltipAddon.db.global.last_cache_update = GetServerTime()
                TitanBistooltipAddon.db.global.last_cache_version = TitanBistooltipAddon.AddonNameAndVersion
                
                return
            end
            
            -- 处理当前批次
            local end_index = math.min(current_index + batch_size - 1, total_classes)
            for i = current_index, end_index do
                local class_name = class_list[i]
                local class_data = TitanBistooltip_bislists[class_name]
                
                for spec_name, spec_data in pairs(class_data) do
                    for phase_name, phase_data in pairs(spec_data) do
                        for _, slot_data in ipairs(phase_data) do
                            for j = 1, 6 do
                                local itemId = slot_data[j]
                                if itemId and itemId ~= -1 then
                                    -- 检查装备是否已经添加到映射表中
                                    if not temp_mapping[itemId] then
                                        temp_mapping[itemId] = {}
                                    end
                                    
                                    -- 检查是否已经添加过相同的职业-专精-槽位组合
                                    local slot_name = slot_data.slot_name
                                    local combo_key = class_name .. "|" .. spec_name .. "|" .. slot_name
                                    
                                    if not temp_mapping[itemId][combo_key] then
                                        temp_mapping[itemId][combo_key] = true
                                        
                                        -- 添加到临时表中
                                        if not temp_items[itemId] then
                                            temp_items[itemId] = {}
                                        end
                                        
                                        table.insert(temp_items[itemId], {
                                            class_name = class_name,
                                            spec_name = spec_name,
                                            slot_name = slot_name
                                        })
                                    end
                                end
                            end
                        end
                    end
                end
            end
            
            -- 更新索引，处理下一批次
            current_index = end_index + 1
            C_Timer.After(0.1, processBatch)
        end
        
        -- 开始处理
        processBatch()
    end
    
    -- 缓存管理函数，避免内存占用过高
    local function manageCache()
        -- 清理排名缓存
        if rank_cache then
            local cache_size = 0
            for _ in pairs(rank_cache) do
                cache_size = cache_size + 1
            end
            
            -- 如果缓存过大，清理一半
            if cache_size > 5000 then
                local count = 0
                local keys_to_remove = {}
                
                -- 收集要删除的键
                for key in pairs(rank_cache) do
                    table.insert(keys_to_remove, key)
                    count = count + 1
                    if count >= cache_size / 2 then
                        break
                    end
                end
                
                -- 批量删除
                for _, key in ipairs(keys_to_remove) do
                    rank_cache[key] = nil
                end
            end
        end
        
        -- 清理装备缓存（只在缓存过大时清理）
        if TitanBistooltip_Titan_items then
            local cache_size = 0
            for _ in pairs(TitanBistooltip_Titan_items) do
                cache_size = cache_size + 1
            end
            
            -- 如果缓存过大，清理最不常用的条目
            -- 缓存过大的定义：超过20000条（考虑到插件只有1600件装备，这个阈值基本上不会触发）
            if cache_size > 20000 then
                local items_with_time = {}
                
                -- 收集所有物品及其最后访问时间
                for itemId, data in pairs(TitanBistooltip_Titan_items) do
                    local last_access_time = data._last_access_time or data._cache_time or 0
                    table.insert(items_with_time, {itemId = itemId, time = last_access_time})
                end
                
                -- 按最后访问时间排序（LRU策略）
                table.sort(items_with_time, function(a, b)
                    return a.time < b.time
                end)
                
                -- 清理最不常用的条目
                local target_count = cache_size - 16000 -- 保留16000条
                for i = 1, math.min(target_count, #items_with_time) do
                    TitanBistooltip_Titan_items[items_with_time[i].itemId] = nil
                end
            end
        end
    end
    
    -- 检查是否需要更新缓存
    local function shouldUpdateCache()
        local current_time = GetServerTime()
        local last_update = TitanBistooltipAddon.db.global.last_cache_update or 0
        local last_version = TitanBistooltipAddon.db.global.last_cache_version or ""
        local current_version = TitanBistooltipAddon.AddonNameAndVersion
        
        -- 检查是否24小时内没有更新过
        local time_diff = current_time - last_update
        local need_time_update = time_diff >= 86400 -- 24小时
        
        -- 检查是否版本有更新
        local need_version_update = last_version ~= current_version
        
        return need_time_update or need_version_update
    end
    
    -- 延迟执行，确保所有数据都已加载
    C_Timer.After(0.5, function()
        -- 检查是否需要更新缓存
        if shouldUpdateCache() then
            -- 更新装备缓存
            updateItemsCache()
        end
        
        -- 自动识别当前角色职业和天赋
        autoDetectClassAndSpec()
        
        -- 执行缓存管理
        manageCache()
    end)
    
    TitanBistooltipAddon:initBisTooltip()
    
    -- 注册事件以在天赋变化时重新识别
    local frame = CreateFrame("Frame")
    frame:RegisterEvent("PLAYER_SPECIALIZATION_CHANGED")
    frame:RegisterEvent("PLAYER_ENTERING_WORLD")
    frame:SetScript("OnEvent", function(self, event)
        -- 延迟执行，确保所有数据都已加载
        C_Timer.After(0.1, function()
            -- 确保数据已经加载
            if not TitanBistooltip_classes or not TitanBistooltip_phases then
                TitanBistooltipAddon:initConfig()
                TitanBistooltipAddon:initBislists()
            end
            autoDetectClassAndSpec()
        end)
    end)
end

function TitanBistooltipAddon:OnEnable()
    -- 插件启用时执行的操作
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00BFFF[快跑兄弟]|r TitanBistooltip 已启用")
    
    -- 确保所有数据都已加载
    C_Timer.After(1, function()
        -- 自动识别当前角色职业和天赋
        autoDetectClassAndSpec()
        
        -- 重新加载数据，确保全局变量和界面更新
        if TitanBistooltipAddon.reloadData then
            TitanBistooltipAddon:reloadData()
        end
        
        -- 应用自动比较装备设置
        if TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.auto_compare_items then
            ConsoleExec("set alwaysCompareItems 1")
        else
            ConsoleExec("set alwaysCompareItems 0")
        end
    end)
end
