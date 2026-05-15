local AceGUI = LibStub("AceGUI-3.0")
local L = LibStub("AceLocale-3.0"):GetLocale("TitanBistooltip", false)

-- 必要的变量定义
local items = {}
local checkmarks = {}
local boemarks = {}


local function clearItemCache()
    for _, checkMark in ipairs(checkmarks) do
        if checkMark and checkMark:GetObjectType() == "Texture" then
            checkMark:Hide()
            checkMark:SetParent(nil)
        end
    end
    for _, boeMark in ipairs(boemarks) do
        if boeMark and boeMark:GetObjectType() == "Texture" then
            boeMark:Hide()
            boeMark:SetParent(nil)
        end
    end
    
    items = {}
    checkmarks = {}
    boemarks = {}
end

local function checkEquipmentByClass(itemId, currentClassName)
    -- 首先检查TitanBistooltip_char_equipment表
    if TitanBistooltip_char_equipment and TitanBistooltip_char_equipment[itemId] ~= nil then
        return true
    end
    
    -- 然后检查玩家是否实际拥有该装备
    -- 通过遍历玩家的装备栏来检查
    for i = 1, 19 do -- 19个装备栏位
        local item
        if C_PlayerInfo and C_PlayerInfo.GetInventoryItemID then
            item = C_PlayerInfo.GetInventoryItemID("player", i)
        else
            item = GetInventoryItemID("player", i)
        end
        if item and item == itemId then
            return true
        end
    end
    
    return false
end



-- 创建物品框体
local function createItemFrame(item_id, size, with_checkmark, parentFrame)
    if item_id < 0 then
        local f = AceGUI:Create("Label")
        f:SetText("") -- 设置为空文本，避免显示默认值
        return f
    end
    local item_frame = AceGUI:Create("Icon")
    item_frame:SetImageSize(size, size)
    items[item_id] = Item:CreateFromItemID(item_id);

    if (items[item_id]:GetItemID()) then
        items[item_id]:ContinueOnItemLoad(function()
            local ilink = items[item_id]:GetItemLink()
            item_frame:SetImage(items[item_id]:GetItemIcon())
            if with_checkmark == true then
                local checkMark = item_frame.frame:CreateTexture(nil, "OVERLAY")
                checkMark:SetWidth(32)
                checkMark:SetHeight(32)
                checkMark:SetPoint("CENTER", 6, -8)
                checkMark:SetTexture("Interface\\AddOns\\TitanBistooltip\\checkmark-16.tga")
                table.insert(checkmarks, checkMark)
            end

            local bindType
            if C_Item and C_Item.GetItemInfo then
                local itemInfo = C_Item.GetItemInfo(item_id)
                if itemInfo then
                    bindType = itemInfo.bindType
                end
            else
                _, _, _, _, _, _, _, _, _, _, _, _, _, bindType = GetItemInfo(item_id)
            end
            if bindType == (LE_ITEM_BIND_ON_EQUIP or 2) then
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
                    local itemName
                    if C_Item and C_Item.GetItemInfo then
                        local itemInfo = C_Item.GetItemInfo(item_id)
                        if itemInfo then
                            itemName = itemInfo.name
                        end
                    else
                        itemName = GetItemInfo(item_id)
                    end
                    if itemName then
                        -- 尝试复制到剪贴板
                        local success = TitanBistooltipAddon:CopyTextToClipboard(itemName)
                    else
                        DEFAULT_CHAT_FRAME:AddMessage("|cffff0000无法获取物品名称|r")
                    end
                end
            end)
            
            -- 保持左键点击功能
            item_frame:SetCallback("OnClick", function(widget, event, button)
                if button == "LeftButton" and ilink then
                    SetItemRef(ilink, ilink, "LeftButton")
                end
            end)
            item_frame:SetCallback("OnEnter", function(widget) 
                if ilink then
                    GameTooltip:ClearLines() -- 清理之前的内容
                    GameTooltip:SetOwner(item_frame.frame, "ANCHOR_NONE") -- 使用ANCHOR_NONE
                    
                    -- 智能调整提示框位置，避免覆盖面板
                    local screenWidth = GetScreenWidth()
                    local frameRight = parentFrame and parentFrame:GetRight() or 0
                    local smartPosition = TitanBistooltipAddon.db.global.tooltip_position
                    
                    if smartPosition and frameRight > screenWidth / 2 then
                        -- 启用智能调整且面板在屏幕右侧，提示框显示在左侧，增加偏移距离避免覆盖
                        GameTooltip:SetPoint("TOPLEFT", item_frame.frame, "TOPLEFT", -300, -13);
                    else
                        -- 未启用智能调整或面板在屏幕左侧，提示框显示在右侧，增加偏移距离避免覆盖
                        GameTooltip:SetPoint("TOPRIGHT", item_frame.frame, "TOPRIGHT", 300, -13);
                    end
                    
                    GameTooltip:SetHyperlink(ilink)
                end
            end)
            item_frame:SetCallback("OnLeave", function(widget) 
                GameTooltip:Hide()
                GameTooltip:ClearLines() -- 清理内容
            end)
        end)
    end
    return item_frame
end

-- 保存框体引用
local maxedFrame = nil

-- 保存毕业装备面板的配置数据
local maxedConfig = {
    class_index = nil,
    spec_index = nil,
    phase_index = nil
}

-- 设置maxedFrame引用
function TitanBistooltipAddon:setMaxedFrameRef(frame)
    maxedFrame = frame
end

-- 关闭毕业装备框体
function TitanBistooltipAddon:closeMaxedFrame()
    if maxedFrame and maxedFrame.frame then
        maxedFrame.frame:Hide()
    end
end

-- 创建毕业装备框体
function TitanBistooltipAddon:showMaxedFrame()
    -- 检查是否已经存在毕业装备框体
    if maxedFrame then
        -- 如果框体已存在，切换其显示/隐藏状态
        if maxedFrame.frame:IsShown() then
            maxedFrame.frame:Hide()
        else
            maxedFrame.frame:Show()
        end
        return
    end
    
    -- 尝试从maxedConfig中获取职业、专精和阶段，如果不存在则从TitanBistooltipAddon配置中获取
    local classIndex = maxedConfig.class_index or TitanBistooltipAddon.db.global.class_index
    local specIndex = maxedConfig.spec_index or TitanBistooltipAddon.db.global.spec_index
    local phaseIndex = maxedConfig.phase_index or TitanBistooltipAddon.db.global.phase_index
    
    -- 保存到maxedConfig
    maxedConfig.class_index = classIndex
    maxedConfig.spec_index = specIndex
    maxedConfig.phase_index = phaseIndex
    
    -- 确保配置数据可用
    if not classIndex or not specIndex or not phaseIndex then
        print("|cffff0000请先选择职业、专精和阶段|r")
        return
    end
    
    -- 确保TitanBistooltip_classes和TitanBistooltip_phases可用
    if not TitanBistooltip_classes or not TitanBistooltip_phases then
        print("|cffff0000无法加载职业和阶段数据|r")
        return
    end
    
    -- 获取当前选择的职业、专精和阶段
    local currentClass = TitanBistooltip_classes[classIndex]
    local currentPhase = TitanBistooltip_phases[phaseIndex]
    
    if not currentClass or not currentPhase then
        print("|cffff0000请先选择职业、专精和阶段|r")
        return
    end
    
    local currentSpec = currentClass.specs[specIndex]
    if not currentSpec then
        print("|cffff0000请先选择职业、专精和阶段|r")
        return
    end
    
    -- 更新全局变量
    TitanBistooltip_class = currentClass.name
    TitanBistooltip_spec = currentSpec
    TitanBistooltip_phase = currentPhase
    
    -- 确保毕业装备数据可用
    if not TitanBistooltip_Maxed_bislists then
        print("|cffff0000无法加载毕业装备数据|r")
        return
    end
    
    local frame = AceGUI:Create("Frame")
    frame:SetWidth(400)
    frame:SetHeight(500)
    frame.frame:SetResizeBounds(400, 400, 400, 500)
    frame:SetTitle("阶段毕业配装")
    frame:SetLayout("List")
    frame:SetCallback("OnClose", function(widget)
        widget.frame:Hide()
    end)
    
    -- 添加OnMove回调，限制框架不能移出游戏界面
    frame:SetCallback("OnMove", function(widget)
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
    frame:SetStatusText("快跑兄弟推荐配装（仅供参考）")
    
    -- 保存框体引用（必须在创建装备之前设置，以便智能提示框位置调整功能正常工作）
    maxedFrame = frame
    
    -- 在右上角添加X按钮
    local xButton = CreateFrame("Button", nil, frame.frame, "UIPanelCloseButton")
    xButton:SetPoint("TOPRIGHT", frame.frame, "TOPRIGHT", -2, -2)
    xButton:SetFrameLevel(frame.frame:GetFrameLevel() + 2)
    xButton:SetHitRectInsets(0, 0, 0, 0)
    xButton:SetScript("OnClick", function(self)
        frame.frame:Hide()
    end)
    frame.xButton = xButton
    
    -- 确保content区域的锚点设置正确
    if frame.content then
        frame.content:SetPoint("BOTTOMRIGHT", -17, 40)
    end
    
    local dropDownGroupRef = nil
    
    -- 设置毕业装备面板位置：显示在主面板左侧，距离1个字体宽度
    if main_frame and main_frame.frame and main_frame.frame:IsShown() then
        local mainX, mainY = main_frame.frame:GetCenter()
        local mainWidth = main_frame.frame:GetWidth()
        local newX = mainX - mainWidth - 12 -- 12像素作为字体宽度的近似值
        frame.frame:SetPoint("CENTER", UIParent, "BOTTOMLEFT", newX, mainY)
    end
    
    local dropDownGroup = AceGUI:Create("SimpleGroup")
    dropDownGroup:SetLayout("Table")
    dropDownGroup:SetUserData("table", {
        columns = { 120, 120, 100 },
        space = 5,
        align = "BOTTOMRIGHT"
    })
    dropDownGroup:SetFullWidth(true)
    dropDownGroup:SetHeight(40)
    frame:AddChild(dropDownGroup)
    dropDownGroupRef = dropDownGroup
    
    local classDropdown = AceGUI:Create("Dropdown")
    
    local class_options = {}
    local class_options_to_class = {}
    for ci, class in ipairs(TitanBistooltip_classes) do
        local option_name = L[class.name]
        table.insert(class_options, option_name)
        class_options_to_class[option_name] = { name = class.name, i = ci }
    end
    
    classDropdown:SetList(class_options)
    classDropdown:SetValue(classIndex)
    classDropdown:SetCallback("OnValueChanged", function(_, _, key)
        local selected_class = class_options_to_class[class_options[key]]
        if selected_class then
            maxedConfig.class_index = selected_class.i
            maxedConfig.spec_index = 1
            TitanBistooltipAddon:updateMaxedFrame()
        end
    end)
    dropDownGroup:AddChild(classDropdown)
    
    local specDropdown = AceGUI:Create("Dropdown")
    
    local spec_options = {}
    local spec_options_to_spec = {}
    for si, spec in ipairs(currentClass.specs) do
        local option_name = L[spec]
        table.insert(spec_options, option_name)
        spec_options_to_spec[option_name] = spec
    end
    
    specDropdown:SetList(spec_options)
    specDropdown:SetValue(specIndex)
    specDropdown:SetCallback("OnValueChanged", function(_, _, key)
        maxedConfig.spec_index = key
        TitanBistooltipAddon:updateMaxedFrame()
    end)
    dropDownGroup:AddChild(specDropdown)
    
    local phaseDropdown = AceGUI:Create("Dropdown")
    phaseDropdown:SetList(TitanBistooltip_phases)
    phaseDropdown:SetValue(phaseIndex)
    phaseDropdown:SetCallback("OnValueChanged", function(_, _, key)
        maxedConfig.phase_index = key
        TitanBistooltipAddon:updateMaxedFrame()
    end)
    dropDownGroup:AddChild(phaseDropdown)
    
    local scrollFrame = AceGUI:Create("ScrollFrame")
    scrollFrame:SetLayout("Table")
    scrollFrame:SetUserData("table", {
        columns = {
            { width = 44 },
            { width = 120 },
            { width = 10 },
            { width = 120 },
            { width = 44 }
        },
        space = 1,
        align = "middle"
    })
    scrollFrame:SetFullWidth(true)
    scrollFrame:SetFullHeight(false)
    scrollFrame:SetAutoAdjustHeight(false)
    frame:AddChild(scrollFrame)
    
    local function updateScrollFrameHeight()
        if frame and frame.frame and dropDownGroupRef then
            local frameHeight = frame.frame:GetHeight()
            local titleBarHeight = 24
            local dropDownHeight = 40
            local statusBarHeight = 24
            local padding = 10
            
            local availableHeight = frameHeight - titleBarHeight - dropDownHeight - statusBarHeight - padding
            availableHeight = math.max(200, availableHeight)
            
            scrollFrame:SetHeight(availableHeight)
        end
    end
    
    updateScrollFrameHeight()
    
    frame.frame:SetScript("OnSizeChanged", updateScrollFrameHeight)
    
    -- 添加每个部位的毕业装备，分成两列显示
    if TitanBistooltip_Maxed_bislists[TitanBistooltip_class] and TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec] then
        -- 获取所有阶段
        local phases = TitanBistooltip_phases
        local currentPhaseIndex = nil
        
        -- 找到当前阶段在phases中的索引
        for i, p in ipairs(phases) do
            if p == TitanBistooltip_phase then
                currentPhaseIndex = i
                break
            end
        end
        
        if currentPhaseIndex then
            -- 尝试获取当前阶段的装备数据，如果不存在则从之前的阶段中查找
            local slots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
            local useBislists = false
            
            -- 如果当前阶段不存在，尝试从之前的阶段中查找
            if not slots then
                for i = currentPhaseIndex - 1, 1, -1 do
                    local prevPhase = phases[i]
                    if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                        slots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                        break
                    end
                end
            end
            
            -- 如果Maxed_bislists中没有数据，尝试从Titan_bislists获取
            if not slots then
                if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                    slots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                    useBislists = true
                else
                    -- 尝试从之前的阶段查找
                    for i = currentPhaseIndex - 1, 1, -1 do
                        local prevPhase = phases[i]
                        if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                            slots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                            useBislists = true
                            break
                        end
                    end
                end
            end
            
            -- 部位名称映射：英文到中文
            local slotNameMap = {
                ["Head"] = "头部",
                ["Neck"] = "颈部",
                ["Shoulder"] = "肩部",
                ["Back"] = "背部",
                ["Chest"] = "胸部",
                ["Wrist"] = "手腕",
                ["Hands"] = "手部",
                ["Waist"] = "腰部",
                ["Legs"] = "腿部",
                ["Feet"] = "脚",
                ["Finger"] = "手指",
                ["Trinket"] = "饰品",
                ["Weapon"] = "主手",
                ["Off hand"] = "副手",
                ["Relic"] = "远程",
                ["Ranged"] = "远程",
                ["Wand"] = "远程"
            }
            
            -- 创建部位到装备ID的映射
            local slotItemMap = {}
            local slotDataMap = {} -- 存储完整的部位数据
            for _, slot in ipairs(slots) do
                local itemId = slot[1]
                local itemId2 = slot[2] -- 用于戒指和饰品的第二个槽位
                local slotName = slot.slot_name
                
                -- 1. 首先从TitanBistooltip_Titan_bislists中查找同一阶段的装备
                if not itemId or itemId <= 0 then
                    if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                        local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                        for _, bisSlot in ipairs(bisSlots) do
                            if bisSlot.slot_name == slotName then
                                itemId = bisSlot[1] -- 取第一件装备
                                if itemId and itemId > 0 then
                                    break
                                end
                            end
                        end
                    end
                end
                
                -- 2. 如果从TitanBistooltip_Titan_bislists中没有找到，或者找到的是-1，从之前的阶段中查找
                if not itemId or itemId <= 0 then
                    for i = currentPhaseIndex - 1, 1, -1 do
                        local prevPhase = phases[i]
                        -- 先从之前阶段的TitanBistooltip_Titan_bislists中查找
                        if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                            local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                            for _, bisSlot in ipairs(bisSlots) do
                                if bisSlot.slot_name == slotName then
                                    itemId = bisSlot[1] -- 取第一件装备
                                    if itemId and itemId > 0 then
                                        break
                                    end
                                end
                            end
                            if itemId and itemId > 0 then
                                break
                            end
                        end
                        -- 再从之前阶段的TitanBistooltip_Maxed_bislists中查找
                        if not itemId or itemId <= 0 then
                            if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                local prevSlots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                for _, prevSlot in ipairs(prevSlots) do
                                    if prevSlot.slot_name == slotName then
                                        itemId = prevSlot[1]
                                        if itemId and itemId > 0 then
                                            break
                                        end
                                    end
                                end
                                if itemId and itemId > 0 then
                                    break
                                end
                            end
                        end
                    end
                end
                
                -- 处理戒指和饰品的第二个槽位
                if (slotName == "Finger" or slotName == "Trinket") then
                    -- 1. 首先从TitanBistooltip_Titan_bislists中查找同一阶段的装备
                    if not itemId2 or itemId2 <= 0 then
                        if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                            local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                            for _, bisSlot in ipairs(bisSlots) do
                                if bisSlot.slot_name == slotName then
                                    itemId2 = bisSlot[2] -- 取第二件装备
                                    if itemId2 and itemId2 > 0 then
                                        break
                                    end
                                end
                            end
                        end
                    end
                    
                    -- 2. 如果从TitanBistooltip_Titan_bislists中没有找到，或者找到的是-1，从之前的阶段中查找
                    if not itemId2 or itemId2 <= 0 then
                        for i = currentPhaseIndex - 1, 1, -1 do
                            local prevPhase = phases[i]
                            -- 先从之前阶段的TitanBistooltip_Titan_bislists中查找
                            if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                for _, bisSlot in ipairs(bisSlots) do
                                    if bisSlot.slot_name == slotName then
                                        itemId2 = bisSlot[2] -- 取第二件装备
                                        if itemId2 and itemId2 > 0 then
                                            break
                                        end
                                    end
                                end
                                if itemId2 and itemId2 > 0 then
                                    break
                                end
                            end
                            -- 再从之前阶段的TitanBistooltip_Maxed_bislists中查找
                            if not itemId2 or itemId2 <= 0 then
                                if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                    local prevSlots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                    for _, prevSlot in ipairs(prevSlots) do
                                        if prevSlot.slot_name == slotName then
                                            itemId2 = prevSlot[2]
                                            if itemId2 and itemId2 > 0 then
                                                break
                                            end
                                        end
                                    end
                                    if itemId2 and itemId2 > 0 then
                                        break
                                    end
                                end
                            end
                        end
                    end
                    -- 更新slot中的第二个槽位装备ID
                    slot[2] = itemId2
                end
                
                -- 更新slot中的装备ID
                slot[1] = itemId
                slotItemMap[slotName] = itemId
                slotDataMap[slotName] = slot -- 存储完整的部位数据
            end
            
            -- 检查主手是否是双手武器（只考虑真正主手槽位的武器）
            local isTwoHandWeapon = false
            local weaponItemId = slotItemMap["Weapon"]
            if weaponItemId and weaponItemId > 0 then
                local equipLoc
                -- GetItemInfo 返回顺序：name, link, quality, itemLevel, reqLevel, class, subclass, maxStack, equipLoc, ...
                equipLoc = select(9, GetItemInfo(weaponItemId))
                
                -- 只判断真正属于主手槽位的双手武器类型
                -- 使用equipLoc（装备位置）判断，这个在所有语言环境下都是英文常量，可靠
                local twoHandEquipLocs = {
                    ["INVTYPE_2HWEAPON"] = true,
                    ["INVTYPE_STAFF"] = true,
                    ["INVTYPE_POLEARM"] = true,
                    ["INVTYPE_2HAXE"] = true,
                    ["INVTYPE_2HSWORD"] = true,
                    ["INVTYPE_2HMACE"] = true,
                    ["INVTYPE_WEAPON2H"] = true,
                    ["INVTYPE_2HWEAPON1"] = true,
                    ["INVTYPE_2HWEAPON2"] = true
                }
                if equipLoc and twoHandEquipLocs[equipLoc] then
                    isTwoHandWeapon = true
                end
            end
            
            -- 判断是否是狂暴战
            local isFuryWarrior = (TitanBistooltip_class == "Warrior" and TitanBistooltip_spec == "Fury")
            
            -- 动态生成左边列的部位列表，跳过没有装备的部位
            -- 如果是双手武器且不是狂暴战，则跳过副手
            local leftSlots = {}
            local leftSlotNames = {"Head", "Neck", "Shoulder", "Back", "Chest", "Wrist", "Weapon", "Off hand", "Relic", "Ranged", "Wand"}
            for _, slot in ipairs(leftSlotNames) do
                -- 如果是副手、主手是双手武器、且不是狂暴战，则跳过
                if slot == "Off hand" and isTwoHandWeapon and not isFuryWarrior then
                    -- 跳过副手
                else
                    local itemId = slotItemMap[slot]
                    if itemId and itemId > 0 then
                        table.insert(leftSlots, slot)
                    end
                end
            end
            
            -- 右边列的部位（英文，用于匹配数据）
            local rightSlots = {
                "Hands", "Waist", "Legs", "Feet", "Finger1", "Finger2", "Trinket1", "Trinket2"
            }
            
            -- 计算需要多少行
            local maxRows = math.max(#leftSlots, #rightSlots)
            
            -- 添加装备到两列
            for i = 1, maxRows do
                -- 左边列
                local leftSlot = leftSlots[i]
                if leftSlot then
                    -- 添加装备
                    local itemId = slotItemMap[leftSlot]
                    if itemId and itemId > 0 then
                        -- 使用与BIS面板相同的方法创建装备框体
                        local hasEquipment = checkEquipmentByClass(itemId, TitanBistooltip_class)
                        
                        if hasEquipment then
                            scrollFrame:AddChild(createItemFrame(itemId, 40, true, maxedFrame.frame))
                        else
                            scrollFrame:AddChild(createItemFrame(itemId, 40, nil, maxedFrame.frame))
                        end
                        
                        -- 添加装备名称（左对齐）
                        local itemInfoLabel = AceGUI:Create("Label")
                        itemInfoLabel:SetWidth(120)
                        itemInfoLabel:SetJustifyH("LEFT")
                        itemInfoLabel:SetText("加载中...")
                        scrollFrame:AddChild(itemInfoLabel)
                        
                        -- 使用Item:CreateFromItemID来确保装备信息加载完成
                        local item = Item:CreateFromItemID(itemId)
                        item:ContinueOnItemLoad(function()
                            local itemName, itemRarity
                            if C_Item and C_Item.GetItemInfoByID then
                                local itemInfo = C_Item.GetItemInfoByID(itemId)
                                if itemInfo then
                                    itemName = itemInfo.name
                                    itemRarity = itemInfo.quality
                                end
                            else
                                itemName, _, itemRarity = GetItemInfo(itemId)
                            end
                            if itemName then
                                -- 设置装备名称，使用装备品质颜色
                                local rarityColor = ITEM_QUALITY_COLORS[itemRarity]
                                if rarityColor then
                                    local coloredName = string.format("|cff%02x%02x%02x%s|r", rarityColor.r * 255, rarityColor.g * 255, rarityColor.b * 255, itemName)
                                    itemInfoLabel:SetText(coloredName)
                                else
                                    itemInfoLabel:SetText(itemName)
                                end
                            else
                                itemInfoLabel:SetText("未知装备")
                            end
                        end)
                    else
                        -- 添加空标签
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                    end
                else
                    -- 添加空标签作为占位符
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                end
                
                -- 间隔列
                scrollFrame:AddChild(AceGUI:Create("Label"))
                
                -- 右边列
                local rightSlot = rightSlots[i]
                if rightSlot then
                    local itemId = nil
                    
                    -- 处理戒指和饰品的两个槽位
                    if rightSlot == "Finger1" then
                        local fingerData = slotDataMap["Finger"]
                        itemId = fingerData and fingerData[1] or nil
                    elseif rightSlot == "Finger2" then
                        local fingerData = slotDataMap["Finger"]
                        itemId = fingerData and fingerData[2] or nil
                    elseif rightSlot == "Trinket1" then
                        local trinketData = slotDataMap["Trinket"]
                        itemId = trinketData and trinketData[1] or nil
                    elseif rightSlot == "Trinket2" then
                        local trinketData = slotDataMap["Trinket"]
                        itemId = trinketData and trinketData[2] or nil
                    else
                        -- 其他部位正常显示
                        itemId = slotItemMap[rightSlot]
                    end
                    
                    if itemId and itemId > 0 then
                        -- 添加装备名称（右对齐）
                        local itemInfoLabel = AceGUI:Create("Label")
                        itemInfoLabel:SetWidth(120)
                        itemInfoLabel:SetJustifyH("RIGHT")
                        itemInfoLabel:SetText("加载中...")
                        scrollFrame:AddChild(itemInfoLabel)
                        
                        -- 添加装备
                        local hasEquipment = checkEquipmentByClass(itemId, TitanBistooltip_class)
                        
                        if hasEquipment then
                            scrollFrame:AddChild(createItemFrame(itemId, 40, true, maxedFrame.frame))
                        else
                            scrollFrame:AddChild(createItemFrame(itemId, 40, nil, maxedFrame.frame))
                        end
                        
                        -- 使用Item:CreateFromItemID来确保装备信息加载完成
                        local item = Item:CreateFromItemID(itemId)
                        item:ContinueOnItemLoad(function()
                            local itemName, itemRarity
                            if C_Item and C_Item.GetItemInfoByID then
                                local itemInfo = C_Item.GetItemInfoByID(itemId)
                                if itemInfo then
                                    itemName = itemInfo.name
                                    itemRarity = itemInfo.quality
                                end
                            else
                                itemName, _, itemRarity = GetItemInfo(itemId)
                            end
                            if itemName then
                                -- 设置装备名称，使用装备品质颜色
                                local rarityColor = ITEM_QUALITY_COLORS[itemRarity]
                                if rarityColor then
                                    local coloredName = string.format("|cff%02x%02x%02x%s|r", rarityColor.r * 255, rarityColor.g * 255, rarityColor.b * 255, itemName)
                                    itemInfoLabel:SetText(coloredName)
                                else
                                    itemInfoLabel:SetText(itemName)
                                end
                            else
                                itemInfoLabel:SetText("未知装备")
                            end
                        end)
                    else
                        -- 添加空标签
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                    end
                else
                    -- 添加空标签作为占位符
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                end
            end
        else
            -- 显示错误信息
            local errorLabel = AceGUI:Create("Label")
            errorLabel:SetText("|cffff0000无法找到阶段数据|r")
            errorLabel:SetUserData("table", { colspan = 5 })
            scrollFrame:AddChild(errorLabel)
        end
    else
        -- 显示错误信息
        local errorLabel = AceGUI:Create("Label")
        errorLabel:SetText("|cffff0000无法找到毕业装备数据|r")
        errorLabel:SetUserData("table", { colspan = 5 })
        scrollFrame:AddChild(errorLabel)
    end
    
    -- 保存框体引用
    maxedFrame = frame
    
    -- 设置状态栏文本
    maxedFrame:SetStatusText("快跑兄弟推荐配装（仅供参考）")
    
    -- 设置maxedFrame引用到TitanBistooltipAddon
    if TitanBistooltipAddon and TitanBistooltipAddon.setMaxedFrameRef then
        TitanBistooltipAddon:setMaxedFrameRef(frame)
    end
    
    -- 显示框体
    frame.frame:Show()
end

-- 更新毕业装备框体
function TitanBistooltipAddon:updateMaxedFrame()
    -- 检查是否存在毕业装备框体
    if not maxedFrame then
        return
    end
    
    -- 强制刷新当前角色装备
    if TitanBistooltip_ScanEquipment then
        TitanBistooltip_ScanEquipment()
    end
    
    if maxedFrame and maxedFrame.frame and maxedFrame.frame.SetResizeBounds then
        maxedFrame.frame:SetResizeBounds(400, 400, 400, 540)
    end
    
    -- 清空物品和标记缓存
    clearItemCache()
    
    -- 尝试从maxedConfig中获取职业、专精和阶段，如果不存在则从TitanBistooltipAddon配置中获取
    local classIndex = maxedConfig.class_index or TitanBistooltipAddon.db.global.class_index
    local specIndex = maxedConfig.spec_index or TitanBistooltipAddon.db.global.spec_index
    local phaseIndex = maxedConfig.phase_index or TitanBistooltipAddon.db.global.phase_index
    
    -- 保存到maxedConfig
    maxedConfig.class_index = classIndex
    maxedConfig.spec_index = specIndex
    maxedConfig.phase_index = phaseIndex
    
    -- 确保配置数据可用
    if not classIndex or not specIndex or not phaseIndex then
        return
    end
    
    -- 确保TitanBistooltip_classes和TitanBistooltip_phases可用
    if not TitanBistooltip_classes or not TitanBistooltip_phases then
        return
    end
    
    -- 获取当前选择的职业、专精和阶段
    local currentClass = TitanBistooltip_classes[classIndex]
    local currentPhase = TitanBistooltip_phases[phaseIndex]
    
    if not currentClass or not currentPhase then
        return
    end
    
    local currentSpec = currentClass.specs[specIndex]
    if not currentSpec then
        return
    end
    
    -- 更新全局变量
    TitanBistooltip_class = currentClass.name
    TitanBistooltip_spec = currentSpec
    TitanBistooltip_phase = currentPhase
    
    -- 更新标题
    maxedFrame:SetTitle("毕业装备")
    maxedFrame:SetStatusText("快跑兄弟推荐配装（仅供参考）")
    -- 确保content区域的锚点设置正确
    if maxedFrame.content then
        maxedFrame.content:SetPoint("BOTTOMRIGHT", -17, 40)
    end
    
    -- 保持当前框架大小，不重置宽度和高度
    -- 这样用户调整宽度后，更换职业、天赋或阶段时会保持用户调整后的宽度
    
    -- 清空内容
    maxedFrame:ReleaseChildren()
    
    -- 重新创建顶部下拉菜单组
    local dropDownGroup = AceGUI:Create("SimpleGroup")
    dropDownGroup:SetLayout("Table")
    dropDownGroup:SetUserData("table", {
        columns = {
            120, 120, 100 },
        space = 5,
        align = "BOTTOMRIGHT"
    })
    dropDownGroup:SetFullWidth(true)
    maxedFrame:AddChild(dropDownGroup)
    
    -- 创建职业下拉菜单
    local classDropdown = AceGUI:Create("Dropdown")
    
    -- 构建职业选项列表，参考Bislist.lua中的实现
    local class_options = {}
    local class_options_to_class = {}
    for ci, class in ipairs(TitanBistooltip_classes) do
        local option_name = L[class.name]
        table.insert(class_options, option_name)
        class_options_to_class[option_name] = { name = class.name, i = ci }
    end
    
    classDropdown:SetList(class_options)
    classDropdown:SetValue(classIndex)
    classDropdown:SetCallback("OnValueChanged", function(_, _, key)
        local selected_class = class_options_to_class[class_options[key]]
        if selected_class then
            maxedConfig.class_index = selected_class.i
            maxedConfig.spec_index = 1 -- 重置专精索引
            TitanBistooltipAddon:updateMaxedFrame()
        end
    end)
    dropDownGroup:AddChild(classDropdown)
    
    -- 创建专精下拉菜单
    local specDropdown = AceGUI:Create("Dropdown")
    
    -- 构建专精选项列表，参考Bislist.lua中的实现
    local spec_options = {}
    local spec_options_to_spec = {}
    for si, spec in ipairs(currentClass.specs) do
        local option_name = L[spec]
        table.insert(spec_options, option_name)
        spec_options_to_spec[option_name] = spec
    end
    
    specDropdown:SetList(spec_options)
    specDropdown:SetValue(specIndex)
    specDropdown:SetCallback("OnValueChanged", function(_, _, key)
        maxedConfig.spec_index = key
        TitanBistooltipAddon:updateMaxedFrame()
    end)
    dropDownGroup:AddChild(specDropdown)
    
    -- 创建阶段下拉菜单
    local phaseDropdown = AceGUI:Create("Dropdown")
    phaseDropdown:SetList(TitanBistooltip_phases)
    phaseDropdown:SetValue(phaseIndex)
    phaseDropdown:SetCallback("OnValueChanged", function(_, _, key)
        maxedConfig.phase_index = key
        TitanBistooltipAddon:updateMaxedFrame()
    end)
    dropDownGroup:AddChild(phaseDropdown)
    
    -- 创建滚动框架，使用两列布局
    local scrollFrame = AceGUI:Create("ScrollFrame")
    scrollFrame:SetLayout("Table")
    scrollFrame:SetUserData("table", {
        columns = {
            { width = 44 },  -- 左边装备图标
            { width = 120 }, -- 左边装备名称
            { width = 10 },  -- 间隔
            { width = 120 }, -- 右边装备名称
            { width = 44 }   -- 右边装备图标
        },
        space = 1,
        align = "middle"
    })
    scrollFrame:SetFullWidth(true)
    scrollFrame:SetFullHeight(false)
    scrollFrame:SetAutoAdjustHeight(false)
    maxedFrame:AddChild(scrollFrame)
    
    -- 添加面板大小变化回调，动态调整滚动框架高度
    local function updateScrollFrameHeight()
        if maxedFrame and maxedFrame.frame then
            local frameHeight = maxedFrame.frame:GetHeight()
            local titleBarHeight = 24 -- 标题栏高度
            local dropDownHeight = 40 -- 下拉菜单组高度
            local statusBarHeight = 24 -- 状态栏高度
            local padding = 10 -- 额外 padding
            
            local availableHeight = frameHeight - titleBarHeight - dropDownHeight - statusBarHeight - padding
            availableHeight = math.max(200, availableHeight) -- 确保最小高度
            
            scrollFrame:SetHeight(availableHeight)
        end
    end
    
    -- 初始计算一次滚动框架高度
    updateScrollFrameHeight()
    
    -- 添加OnSizeChanged回调
    maxedFrame.frame:SetScript("OnSizeChanged", updateScrollFrameHeight)
    
    -- 添加每个部位的毕业装备，分成两列显示
    if TitanBistooltip_Maxed_bislists[TitanBistooltip_class] and TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec] then
        -- 获取所有阶段
        local phases = TitanBistooltip_phases
        local currentPhaseIndex = nil
        
        -- 找到当前阶段在phases中的索引
        for i, p in ipairs(phases) do
            if p == TitanBistooltip_phase then
                currentPhaseIndex = i
                break
            end
        end
        
        if currentPhaseIndex then
            -- 尝试获取当前阶段的装备数据，如果不存在则从之前的阶段中查找
            local slots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
            local useBislists = false
            
            -- 如果当前阶段不存在，尝试从之前的阶段中查找
            if not slots then
                for i = currentPhaseIndex - 1, 1, -1 do
                    local prevPhase = phases[i]
                    if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                        slots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                        break
                    end
                end
            end
            
            -- 如果Maxed_bislists中没有该天赋数据，从Titan_bislists获取
            if not slots then
                if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] then
                    if TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                        slots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                        useBislists = true
                    else
                        -- 尝试从之前的阶段查找
                        for i = currentPhaseIndex - 1, 1, -1 do
                            local prevPhase = phases[i]
                            if TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                slots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                useBislists = true
                                break
                            end
                        end
                    end
                end
            end
            
            -- 部位名称映射：英文到中文
            local slotNameMap = {
                ["Head"] = "头部",
                ["Neck"] = "颈部",
                ["Shoulder"] = "肩部",
                ["Back"] = "背部",
                ["Chest"] = "胸部",
                ["Wrist"] = "手腕",
                ["Hands"] = "手部",
                ["Waist"] = "腰部",
                ["Legs"] = "腿部",
                ["Feet"] = "脚",
                ["Finger"] = "手指",
                ["Trinket"] = "饰品",
                ["Weapon"] = "主手",
                ["Off hand"] = "副手",
                ["Relic"] = "远程",
                ["Ranged"] = "远程",
                ["Wand"] = "远程"
            }
            
            -- 创建部位到装备ID的映射
            local slotItemMap = {}
            local slotDataMap = {} -- 存储完整的部位数据
            for _, slot in ipairs(slots) do
                local itemId = slot[1]
                local itemId2 = slot[2] -- 用于戒指和饰品的第二个槽位
                local slotName = slot.slot_name
                
                -- 如果当前阶段的装备是-1，首先从TitanBistooltip_Titan_bislists中查找同一阶段的装备
                if not itemId or itemId <= 0 then
                    -- 1. 首先从TitanBistooltip_Titan_bislists中查找同一阶段的装备
                    if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                        local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                        for _, bisSlot in ipairs(bisSlots) do
                            if bisSlot.slot_name == slotName then
                                itemId = bisSlot[1] -- 取第一件装备
                                if itemId and itemId > 0 then
                                    break
                                end
                            end
                        end
                    end
                    
                    -- 2. 如果从TitanBistooltip_Titan_bislists中没有找到，或者找到的是-1，从之前的阶段中查找
                    if not itemId or itemId <= 0 then
                        for i = currentPhaseIndex - 1, 1, -1 do
                            local prevPhase = phases[i]
                            if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                local prevSlots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                for _, prevSlot in ipairs(prevSlots) do
                                    if prevSlot.slot_name == slotName then
                                        itemId = prevSlot[1]
                                        if itemId and itemId > 0 then
                                            break
                                        end
                                    end
                                end
                                if itemId and itemId > 0 then
                                    break
                                end
                            end
                        end
                    end
                end
                
                -- 处理戒指和饰品的第二个槽位
                if (slotName == "Finger" or slotName == "Trinket") then
                    if not itemId2 or itemId2 <= 0 then
                        -- 1. 首先从TitanBistooltip_Titan_bislists中查找同一阶段的装备
                        if TitanBistooltip_Titan_bislists[TitanBistooltip_class] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec] and TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase] then
                            local bisSlots = TitanBistooltip_Titan_bislists[TitanBistooltip_class][TitanBistooltip_spec][TitanBistooltip_phase]
                            for _, bisSlot in ipairs(bisSlots) do
                                if bisSlot.slot_name == slotName then
                                    itemId2 = bisSlot[2] -- 取第二件装备
                                    if itemId2 and itemId2 > 0 then
                                        break
                                    end
                                end
                            end
                        end
                        
                        -- 2. 如果从TitanBistooltip_Titan_bislists中没有找到，或者找到的是-1，从之前的阶段中查找
                        if not itemId2 or itemId2 <= 0 then
                            for i = currentPhaseIndex - 1, 1, -1 do
                                local prevPhase = phases[i]
                                if TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase] then
                                    local prevSlots = TitanBistooltip_Maxed_bislists[TitanBistooltip_class][TitanBistooltip_spec][prevPhase]
                                    for _, prevSlot in ipairs(prevSlots) do
                                        if prevSlot.slot_name == slotName then
                                            itemId2 = prevSlot[2]
                                            if itemId2 and itemId2 > 0 then
                                                break
                                            end
                                        end
                                    end
                                    if itemId2 and itemId2 > 0 then
                                        break
                                    end
                                end
                            end
                        end
                    end
                    -- 更新slot中的第二个槽位装备ID
                    slot[2] = itemId2
                end
                
                -- 更新slot中的装备ID
                slot[1] = itemId
                slotItemMap[slotName] = itemId
                slotDataMap[slotName] = slot -- 存储完整的部位数据
            end
            
            -- 检查主手是否是双手武器（只考虑真正主手槽位的武器）
            local isTwoHandWeapon = false
            local weaponItemId = slotItemMap["Weapon"]
            if weaponItemId and weaponItemId > 0 then
                local equipLoc
                -- GetItemInfo 返回顺序：name, link, quality, itemLevel, reqLevel, class, subclass, maxStack, equipLoc, ...
                equipLoc = select(9, GetItemInfo(weaponItemId))
                
                -- 只判断真正属于主手槽位的双手武器类型
                -- 使用equipLoc（装备位置）判断，这个在所有语言环境下都是英文常量，可靠
                local twoHandEquipLocs = {
                    ["INVTYPE_2HWEAPON"] = true,
                    ["INVTYPE_STAFF"] = true,
                    ["INVTYPE_POLEARM"] = true,
                    ["INVTYPE_2HAXE"] = true,
                    ["INVTYPE_2HSWORD"] = true,
                    ["INVTYPE_2HMACE"] = true,
                    ["INVTYPE_WEAPON2H"] = true
                }
                if equipLoc and twoHandEquipLocs[equipLoc] then
                    isTwoHandWeapon = true
                end
            end
            
            -- 判断是否是狂暴战
            local isFuryWarrior = (TitanBistooltip_class == "Warrior" and TitanBistooltip_spec == "Fury")
            
            -- 动态生成左边列的部位列表，跳过没有装备的部位
            -- 如果是双手武器且不是狂暴战，则跳过副手
            local leftSlots = {}
            local leftSlotNames = {"Head", "Neck", "Shoulder", "Back", "Chest", "Wrist", "Weapon", "Off hand", "Relic", "Ranged", "Wand"}
            for _, slot in ipairs(leftSlotNames) do
                -- 如果是副手、主手是双手武器、且不是狂暴战，则跳过
                if slot == "Off hand" and isTwoHandWeapon and not isFuryWarrior then
                    -- 跳过副手
                else
                    local itemId = slotItemMap[slot]
                    if itemId and itemId > 0 then
                        table.insert(leftSlots, slot)
                    end
                end
            end
            
            -- 右边列的部位（英文，用于匹配数据）
            local rightSlots = {
                "Hands", "Waist", "Legs", "Feet", "Finger1", "Finger2", "Trinket1", "Trinket2"
            }
            
            -- 计算需要多少行
            local maxRows = math.max(#leftSlots, #rightSlots)
            
            -- 添加装备到两列
            for i = 1, maxRows do
                -- 左边列
                local leftSlot = leftSlots[i]
                if leftSlot then
                    -- 添加装备
                    local itemId = slotItemMap[leftSlot]
                    if itemId and itemId > 0 then
                        -- 使用与BIS面板相同的方法创建装备框体
                        local hasEquipment = checkEquipmentByClass(itemId, TitanBistooltip_class)
                        
                        if hasEquipment then
                            scrollFrame:AddChild(createItemFrame(itemId, 40, true, maxedFrame.frame))
                        else
                            scrollFrame:AddChild(createItemFrame(itemId, 40, nil, maxedFrame.frame))
                        end
                        
                        -- 添加装备名称（左对齐）
                        local itemInfoLabel = AceGUI:Create("Label")
                        itemInfoLabel:SetWidth(120)
                        itemInfoLabel:SetJustifyH("LEFT")
                        itemInfoLabel:SetText("加载中...")
                        scrollFrame:AddChild(itemInfoLabel)
                        
                        -- 使用Item:CreateFromItemID来确保装备信息加载完成
                        local item = Item:CreateFromItemID(itemId)
                        item:ContinueOnItemLoad(function()
                            local itemName, itemRarity
                            if C_Item and C_Item.GetItemInfoByID then
                                local itemInfo = C_Item.GetItemInfoByID(itemId)
                                if itemInfo then
                                    itemName = itemInfo.name
                                    itemRarity = itemInfo.quality
                                end
                            else
                                itemName, _, itemRarity = GetItemInfo(itemId)
                            end
                            if itemName then
                                -- 设置装备名称，使用装备品质颜色
                                local rarityColor = ITEM_QUALITY_COLORS[itemRarity]
                                if rarityColor then
                                    local coloredName = string.format("|cff%02x%02x%02x%s|r", rarityColor.r * 255, rarityColor.g * 255, rarityColor.b * 255, itemName)
                                    itemInfoLabel:SetText(coloredName)
                                else
                                    itemInfoLabel:SetText(itemName)
                                end
                            else
                                itemInfoLabel:SetText("未知装备")
                            end
                        end)
                    else
                        -- 添加空标签
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                    end
                else
                    -- 添加空标签作为占位符
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                end
                
                -- 间隔列
                scrollFrame:AddChild(AceGUI:Create("Label"))
                
                -- 右边列
                local rightSlot = rightSlots[i]
                if rightSlot then
                    local itemId = nil
                    
                    -- 处理戒指和饰品的两个槽位
                    if rightSlot == "Finger1" then
                        local fingerData = slotDataMap["Finger"]
                        itemId = fingerData and fingerData[1] or nil
                    elseif rightSlot == "Finger2" then
                        local fingerData = slotDataMap["Finger"]
                        itemId = fingerData and fingerData[2] or nil
                    elseif rightSlot == "Trinket1" then
                        local trinketData = slotDataMap["Trinket"]
                        itemId = trinketData and trinketData[1] or nil
                    elseif rightSlot == "Trinket2" then
                        local trinketData = slotDataMap["Trinket"]
                        itemId = trinketData and trinketData[2] or nil
                    else
                        -- 其他部位正常显示
                        itemId = slotItemMap[rightSlot]
                    end
                    
                    if itemId and itemId > 0 then
                        -- 添加装备名称（右对齐）
                        local itemInfoLabel = AceGUI:Create("Label")
                        itemInfoLabel:SetWidth(120)
                        itemInfoLabel:SetJustifyH("RIGHT")
                        itemInfoLabel:SetText("加载中...")
                        scrollFrame:AddChild(itemInfoLabel)
                        
                        -- 添加装备
                        local hasEquipment = checkEquipmentByClass(itemId, TitanBistooltip_class)
                        
                        if hasEquipment then
                            scrollFrame:AddChild(createItemFrame(itemId, 40, true, maxedFrame.frame))
                        else
                            scrollFrame:AddChild(createItemFrame(itemId, 40, nil, maxedFrame.frame))
                        end
                        
                        -- 使用Item:CreateFromItemID来确保装备信息加载完成
                        local item = Item:CreateFromItemID(itemId)
                        item:ContinueOnItemLoad(function()
                            local itemName, itemRarity
                            if C_Item and C_Item.GetItemInfoByID then
                                local itemInfo = C_Item.GetItemInfoByID(itemId)
                                if itemInfo then
                                    itemName = itemInfo.name
                                    itemRarity = itemInfo.quality
                                end
                            else
                                itemName, _, itemRarity = GetItemInfo(itemId)
                            end
                            if itemName then
                                -- 设置装备名称，使用装备品质颜色
                                local rarityColor = ITEM_QUALITY_COLORS[itemRarity]
                                if rarityColor then
                                    local coloredName = string.format("|cff%02x%02x%02x%s|r", rarityColor.r * 255, rarityColor.g * 255, rarityColor.b * 255, itemName)
                                    itemInfoLabel:SetText(coloredName)
                                else
                                    itemInfoLabel:SetText(itemName)
                                end
                            else
                                itemInfoLabel:SetText("未知装备")
                            end
                        end)
                    else
                        -- 添加空标签
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                        scrollFrame:AddChild(AceGUI:Create("Label"))
                    end
                else
                    -- 添加空标签作为占位符
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                    scrollFrame:AddChild(AceGUI:Create("Label"))
                end
            end
        else
            -- 显示错误信息
            local errorLabel = AceGUI:Create("Label")
            errorLabel:SetText("|cffff0000无法找到阶段数据|r")
            errorLabel:SetUserData("table", { colspan = 5 })
            scrollFrame:AddChild(errorLabel)
        end
    else
        -- 显示错误信息
        local errorLabel = AceGUI:Create("Label")
        errorLabel:SetText("|cffff0000无法找到毕业装备数据|r")
        errorLabel:SetUserData("table", { colspan = 5 })
        scrollFrame:AddChild(errorLabel)
    end
end

-- 延迟注册函数到TitanBistooltipAddon，确保对象已经创建
local function registerFunctions()
    if TitanBistooltipAddon then
        TitanBistooltipAddon.showMaxedFrame = TitanBistooltipAddon.showMaxedFrame or showMaxedFrame
        TitanBistooltipAddon.updateMaxedFrame = TitanBistooltipAddon.updateMaxedFrame or updateMaxedFrame
    else
        -- 如果TitanBistooltipAddon还没有创建，延迟1秒后再尝试
        C_Timer.After(1, registerFunctions)
    end
end

-- 开始注册
registerFunctions()
