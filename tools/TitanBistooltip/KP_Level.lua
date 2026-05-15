-- KP_Level.lua
-- 快跑兄弟的整合装备等级显示功能：
-- 1. 角色属性界面装备等级显示
-- 2. 装备提示框装备和其它物品等级显示
-- 3. 背包里的装备上显示装备等级

local CharacterItemLevel = {}

-- ==================== 角色属性界面装备等级显示 ====================

local SGFrames = {}
local SGStrings = {}
local SGSlots = {
	{CharacterHeadSlot,"HeadSlot"},
	{CharacterNeckSlot,"NeckSlot"},
	{CharacterShoulderSlot,"ShoulderSlot"},
	{CharacterBackSlot,"BackSlot"},
	{CharacterChestSlot,"ChestSlot"},
	{CharacterWristSlot,"WristSlot"},
	{CharacterMainHandSlot,"MainHandSlot"},
	{CharacterSecondaryHandSlot,"SecondaryHandSlot"},
	{CharacterRangedSlot,"RangedSlot"},
	{CharacterHandsSlot,"HandsSlot"},
	{CharacterWaistSlot,"WaistSlot"},
	{CharacterLegsSlot,"LegsSlot"},
	{CharacterFeetSlot,"FeetSlot"},
	{CharacterFinger0Slot,"Finger0Slot"},
	{CharacterFinger1Slot,"Finger1Slot"},
	{CharacterTrinket0Slot,"Trinket0Slot"},
	{CharacterTrinket1Slot,"Trinket1Slot"}
}

local function CreateFrames()
	for i=1,17 do
		SGFrames[i] = CreateFrame("Frame",nil,SGSlots[i][1])
		SGFrames[i]:SetWidth(SGSlots[i][1]:GetWidth())
		SGFrames[i]:SetHeight(SGSlots[i][1]:GetHeight())
		SGFrames[i]:SetPoint("CENTER",0,0)
		SGStrings[i] = SGFrames[i]:CreateFontString(nil, "OVERLAY")
		SGStrings[i]:SetPoint("BOTTOM", 0, 2)
		SGStrings[i]:SetJustifyH("CENTER")
		SGStrings[i]:SetFontObject(NumberFont_Outline_Med or NumberFontNormal)
		SGStrings[i]:SetShadowOffset(1, -1)
		SGStrings[i]:SetShadowColor(0, 0, 0, .5)
		SGStrings[i]:SetText("")
	end
end

local function UpdateCharacterFrames()
	if not TitanBistooltipAddon or not TitanBistooltipAddon.db or not TitanBistooltipAddon.db.global.show_character_item_level then
		for i=1,17 do
			SGStrings[i]:SetText("")
		end
		return
	end
	
	for i=1,17 do
		local iid = GetInventoryItemID("player", GetInventorySlotInfo(SGSlots[i][2]))
		if type(iid) == "nil" then
			SGStrings[i]:SetText("")
		else
			-- 获取物品链接
			local itemLink = GetInventoryItemLink("player", GetInventorySlotInfo(SGSlots[i][2]))
			-- 获取物品品质（GetItemInfo返回的第3个值）
			local _, _, itemQuality = GetItemInfo(iid)
			-- 获取装备等级
			local itemLevel = GetDetailedItemLevelInfo(itemLink)
			if not itemLevel then
				_, _, itemLevel = GetItemInfo(iid)
			end
			
			if type(itemLevel) == "nil" then
				SGStrings[i]:SetText("")
			else
				SGStrings[i]:SetText(itemLevel)
				-- 根据物品品质设置颜色
				local qualityColor = ITEM_QUALITY_COLORS[itemQuality] or ITEM_QUALITY_COLORS[1]
				SGStrings[i]:SetTextColor(qualityColor.r, qualityColor.g, qualityColor.b)
			end
		end
	end
end

-- 暴露为全局函数，供Config.lua调用
TitanBistooltip_UpdateCharacterItemLevel = UpdateCharacterFrames
CharacterItemLevel.UpdateCharacterFrames = UpdateCharacterFrames

-- ==================== 装备提示框装备等级显示 ====================

local function AddItemLevelToTooltip(tooltip)
	if not TitanBistooltipAddon or not TitanBistooltipAddon.db or not TitanBistooltipAddon.db.global.show_item_level_tooltip then
		return
	end
	
	local _, link = tooltip:GetItem()
	if not link then
		return
	end
	
	-- 检查是否是假的物品链接（item:3299是按ALT键时使用的）
	if string.find(link, "item:3299") then
		return
	end
	
	-- 获取装备等级
	local itemLevel = GetDetailedItemLevelInfo(link)
	if not itemLevel then
		_, _, itemLevel = GetItemInfo(link)
	end
	
	if itemLevel and itemLevel ~= 1 then
		-- 获取装备品质颜色
		local _, _, itemQuality = GetItemInfo(link)
		local qualityColor = ITEM_QUALITY_COLORS[itemQuality] or ITEM_QUALITY_COLORS[1]
		
		-- 获取左行的字号
		local leftLine = _G[tooltip:GetName() .. "TextLeft1"]
		local _, fontHeight, _
		if leftLine then
			_, fontHeight, _ = leftLine:GetFont()
		end
		
		-- 修改右行
		local rightLine = _G[tooltip:GetName() .. "TextRight1"]
		if rightLine then
			-- 设置文本
			rightLine:SetText(itemLevel)
			-- 设置颜色（根据物品品质）
			rightLine:SetTextColor(qualityColor.r, qualityColor.g, qualityColor.b)
			-- 设置右对齐
			rightLine:SetJustifyH("RIGHT")
			-- 设置字号和左行一致
			if fontHeight then
				local fontName, _, fontFlags = rightLine:GetFont()
				rightLine:SetFont(fontName, fontHeight, fontFlags)
			end
			rightLine:Show()
		end
	end
end

-- ==================== 事件处理 ====================

local function OnEvent(self, event, ...)
	UpdateCharacterFrames()
end

local frame = CreateFrame("Frame")
CreateFrames()
frame:SetScript("OnEvent", OnEvent)
frame:RegisterEvent("BAG_UPDATE")
frame:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")

-- 延迟更新确保装备信息已加载
local delayFrame = CreateFrame("Frame")
delayFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
delayFrame:SetScript("OnEvent", function(self, event)
    self:UnregisterEvent(event)
    C_Timer.After(1, function()
        UpdateCharacterFrames()
    end)
end)

-- 角色面板打开时更新
	if CharacterFrame then
		hooksecurefunc(CharacterFrame, "Show", UpdateCharacterFrames)
	end



-- ==================== 装备提示框钩子注册 ====================

local function RegisterTooltipHooks()
	local tooltips = {
		["GameTooltip"] = true,
		["ShoppingTooltip1"] = true,
		["ShoppingTooltip2"] = true,
		["ItemRefTooltip"] = true,
		["ItemRefShoppingTooltip1"] = true,
		["ItemRefShoppingTooltip2"] = true,
		["AtlasLootTooltip"] = true,
	}

	for tooltipName in pairs(tooltips) do
		local tooltip = _G[tooltipName]
		if tooltip then
			tooltip:HookScript("OnTooltipSetItem", AddItemLevelToTooltip)
		end
	end
end

-- 在 ADDON_LOADED 事件后注册钩子，确保 TitanBistooltipAddon 已初始化
local initFrame = CreateFrame("Frame")
initFrame:RegisterEvent("ADDON_LOADED")
initFrame:SetScript("OnEvent", function(self, event, addonName)
	if addonName == "TitanBistooltip" then
		self:UnregisterEvent(event)
		RegisterTooltipHooks()
	end
end)

return CharacterItemLevel
