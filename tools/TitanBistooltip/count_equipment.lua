-- 统计装备数量的脚本
local function CountEquipment()
    local totalEquipment = 0
    local equipmentSet = {}
    
    -- 遍历所有职业
    for className, classData in pairs(TitanBistooltip_Titan_bislists) do
        -- 遍历每个职业的专精
        for specName, specData in pairs(classData) do
            -- 遍历每个专精的阶段
            for phaseName, phaseData in pairs(specData) do
                -- 遍历每个阶段的装备槽位
                for slotIndex, slotData in pairs(phaseData) do
                    -- 遍历槽位中的装备ID（从1到6）
                    for i = 1, 6 do
                        local itemId = slotData[i]
                        if itemId and itemId > 0 then
                            -- 使用装备ID作为键，确保不重复计数
                            equipmentSet[itemId] = true
                        end
                    end
                end
            end
        end
    end
    
    -- 计算唯一装备数量
    for itemId in pairs(equipmentSet) do
        totalEquipment = totalEquipment + 1
    end
    
    print("数据库中装备总数: " .. totalEquipment)
    return totalEquipment
end

-- 执行统计
CountEquipment()