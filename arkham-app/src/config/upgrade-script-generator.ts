/**
 * Represents a 2D coordinate pair.
 */
type Coordinate = [number, number];

/**
 * Represents a row of checkboxes, grouped by their y-coordinate.
 */
interface CheckboxRow {
    y: number;
    xCoords: number[];
}

/**
 * Contains the calculated layout parameters for the Lua script.
 */
interface LuaLayoutParams {
    xInitial: number;
    xOffset: number;
    customizations: string;
}

/**
 * 使用你提供的真实坐标作为校准参考
 * 基于你之前提到的: [68, 206] 是第一个复选框, [89, 580] 是另一个复选框
 */
const CALIBRATION_DATA = {
    // 从原始 Power Word 脚本中已知的参数
    originalXInitial: -0.933,
    originalXOffset: 0.069,

    // 校准参考点 - 这些需要根据实际情况调整
    // 假设 [68, 206] 对应第一行第一个复选框
    referencePixel1: { x: 68, y: 206 },
    referenceLogic1: {
        x: -0.933 + 1 * 0.069, // -0.864
        z: -0.905 // 假设是第一行
    },

    // 假设 [89, 580] 对应第五行第二个复选框  
    referencePixel2: { x: 89, y: 580 },
    referenceLogic2: {
        x: -0.933 + 2 * 0.069, // -0.795
        z: 0.18 // 第五行的posZ
    }
};

/**
 * 计算坐标转换参数
 */
function calculateTransformParams() {
    const { referencePixel1, referenceLogic1, referencePixel2, referenceLogic2 } = CALIBRATION_DATA;

    // 计算缩放系数
    const scaleX = (referencePixel2.x - referencePixel1.x) / (referenceLogic2.x - referenceLogic1.x);
    const scaleY = (referencePixel2.y - referencePixel1.y) / (referenceLogic2.z - referenceLogic1.z);

    // 计算偏移量
    const offsetX = referencePixel1.x - scaleX * referenceLogic1.x;
    const offsetY = referencePixel1.y - scaleY * referenceLogic1.z;

    return { scaleX, scaleY, offsetX, offsetY };
}

/**
 * 生成 Lua 布局参数 - 只修改坐标计算，保持其他逻辑不变
 */
function generateLuaLayoutParams(coordinates: Coordinate[]): LuaLayoutParams {
    if (!coordinates || coordinates.length === 0) {
        throw new Error("Coordinate array cannot be empty.");
    }

    // 按 Y 坐标分组形成行
    const rowMap = new Map<number, number[]>();
    for (const [x, y] of coordinates) {
        if (!rowMap.has(y)) {
            rowMap.set(y, []);
        }
        rowMap.get(y)!.push(x);
    }

    // 转换为行对象并排序
    const sortedRows: CheckboxRow[] = Array.from(rowMap.entries())
        .map(([y, xCoords]) => ({
            y,
            xCoords: xCoords.sort((a, b) => a - b),
        }))
        .sort((a, b) => a.y - b.y);

    // 计算转换参数
    const { scaleX, scaleY, offsetX, offsetY } = calculateTransformParams();

    // const scaleX = 41.9287211740;

    // 计算第一个复选框的逻辑坐标
    const firstPixelX = sortedRows[0].xCoords[0];
    const firstLogicX = (firstPixelX - offsetX) / scaleX;

    // 计算像素间距对应的逻辑间距
    let pixelXOffset = 40; // 默认值
    for (const row of sortedRows) {
        if (row.xCoords.length > 1) {
            pixelXOffset = row.xCoords[1] - row.xCoords[0];
            break;
        }
    }
    console.log('像素间距', pixelXOffset, scaleX);

    const logicXOffset = pixelXOffset / 350.287211740;

    // 计算 xInitial (第一列对应 xInitial + xOffset)
    const xInitial = firstLogicX - logicXOffset;
    const xOffset = logicXOffset;

    // 生成 customizations 表
    const customizationsEntries = sortedRows.map((row, index) => {
        const luaRowIndex = index + 1;
        const count = row.xCoords.length;
        const posZ = (row.y - offsetY) / scaleY;

        return `  [${luaRowIndex}] = {\n    checkboxes = {\n      posZ = ${posZ.toFixed(4)},\n      count = ${count},\n    }\n  }`;
    });

    const customizations = `customizations = {\n${customizationsEntries.join(',\n')}\n}`;

    return {
        xInitial,
        xOffset,
        customizations,
    };
}

/**
 * 创建完整的 Lua 脚本 - 完全保持原有结构，只替换坐标参数
 */
export function generateUpgradePowerWordScript(checkboxCoordinates: Coordinate[]): string {
    const { xInitial, xOffset, customizations } = generateLuaLayoutParams(checkboxCoordinates);

    // 使用完全相同的原始脚本结构，只替换坐标参数
    return `-- Bundled by luabundle {"version":"1.6.0"}
local __bundle_require, __bundle_loaded, __bundle_register, __bundle_modules = (function(superRequire)
	local loadingPlaceholder = {[{}] = true}

	local register
	local modules = {}

	local require
	local loaded = {}

	register = function(name, body)
		if not modules[name] then
			modules[name] = body
		end
	end

	require = function(name)
		local loadedModule = loaded[name]

		if loadedModule then
			if loadedModule == loadingPlaceholder then
				return nil
			end
		else
			if not modules[name] then
				if not superRequire then
					local identifier = type(name) == 'string' and '\"' .. name .. '\"' or tostring(name)
					error('Tried to require ' .. identifier .. ', but no such module has been registered')
				else
					return superRequire(name)
				end
			end

			loaded[name] = loadingPlaceholder
			loadedModule = modules[name](require, loaded, register, modules)
			loaded[name] = loadedModule
		end

		return loadedModule
	end

	return require, loaded, register, modules
end)(nil)
__bundle_register("__root", function(require, _LOADED, __bundle_register, __bundle_modules)
require("playercards/customizable/PowerWordUpgradeSheetTaboo")
end)
__bundle_register("core/GUIDReferenceApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local GUIDReferenceApi = {}

  local function callhandler(functionName, argument)
    return getObjectFromGUID("123456").call(functionName, argument)
  end

  -- General information:
  --- "owner" is a string that describes the parent object
  --- "type" is a string that describes the type of object

  -- Returns the matching object
  function GUIDReferenceApi.getObjectByOwnerAndType(owner, type)
    return callhandler("getObjectByOwnerAndType", { owner = owner, type = type })
  end

  -- Returns all matching objects as a table with references
  function GUIDReferenceApi.getObjectsByType(type)
    return callhandler("getObjectsByType", type)
  end

  -- Returns all matching objects as a table with references
  function GUIDReferenceApi.getObjectsByOwner(owner)
    return callhandler("getObjectsByOwner", owner)
  end

  -- Sends new information to the reference handler to edit the main index (if type/guid are omitted, entry will be removed)
  function GUIDReferenceApi.editIndex(owner, type, guid)
    return callhandler("editIndex", { owner = owner, type = type, guid = guid })
  end

  -- Returns the owner of an object or the object it's located on
  function GUIDReferenceApi.getOwnerOfObject(object)
    return callhandler("getOwnerOfObject", object)
  end

  function GUIDReferenceApi.removeObjectByOwnerAndType(owner, type)
    return callhandler("removeObjectByOwnerAndType", { owner = owner, type = type })
  end

  return GUIDReferenceApi
end
end)
__bundle_register("playercards/customizable/PowerWordUpgradeSheetTaboo", function(require, _LOADED, __bundle_register, __bundle_modules)
-- Customizable Cards: Power Word (Taboo)
-- Generated with custom coordinates

-- Color information for buttons
boxSize = 38

-- static values (auto-generated from pixel coordinates)
xInitial = ${xInitial.toFixed(4)}
xOffset  = ${xOffset.toFixed(4)}

${customizations}

require("playercards/customizable/UpgradeSheetLibrary")
end)
__bundle_register("playercards/customizable/UpgradeSheetLibrary", function(require, _LOADED, __bundle_register, __bundle_modules)
-- Common code for handling customizable card upgrade sheets
-- Define UI elements in the base card file, then include this
-- UI element definition is an array of tables, each with this structure. A row may include
-- checkboxes (number defined by count), a text field, both, or neither (if the row has custom
-- handling, as Living Ink does)
-- {
--   checkboxes = {
--     posZ = -0.71,
--     count = 1
--   },
--   textField = {
--     position =  { 0.005, 0.25, -0.58 },
--     width = 875
--   }
-- }
-- Fields should also be defined for xInitial (left edge of the checkboxes) and xOffset (amount to
-- shift X from one box to the next) as well as boxSize (checkboxes) and inputFontSize.
--
-- selectedUpgrades holds the state of checkboxes and text input, each element being:
-- selectedUpgrades[row] = { xp = #, text = "" }

local MathLib                        = require("util/MathLib")
local PlayermatApi                   = require("playermat/PlayermatApi")

-- Y position for UI elements
local Y_VISIBLE                      = 0.25

-- Variable to check whether UI finished loading
local isLoading                      = true

-- Used for Summoned Servitor and Living Ink
local VECTOR_COLOR                   = {
  unselected = { 0.5, 0.5, 0.5, 0.75 },
  mystic     = { 0.597, 0.195, 0.796 }
}

-- These match with ArkhamDB's way of storing the data in the dropdown menu
local SUMMONED_SERVITOR_SLOT_INDICES = { arcane = "1", ally = "0", none = "" }

-- Unicode Characters used for the checkboxes
local CHECKBOX_CHARS                 = { 10007, 10008 }

local selectedUpgrades               = {}

function updateSave()
  self.script_state = JSON.encode({ selections = selectedUpgrades })
end

-- Startup procedure
function onLoad(savedData)
  if savedData and savedData ~= "" then
    local loadedData = JSON.decode(savedData)
    if loadedData.selections ~= nil then
      selectedUpgrades = loadedData.selections
    end
  end

  selfId = getSelfId()
  maybeLoadLivingInkSkills()
  xmlTable = {}
  createUi()
  maybeUpdateLivingInkSkillDisplay()
  maybeUpdateServitorSlotDisplay()

  self.addContextMenuItem("Clear Selections", function() resetSelections() end)
  self.addContextMenuItem("Scale: 1x", function() self.setScale({ 1, 1, 1 }) end)
  self.addContextMenuItem("Scale: 2x", function() self.setScale({ 2, 1, 2 }) end)
  self.addContextMenuItem("Scale: 3x", function() self.setScale({ 3, 1, 3 }) end)
end

-- Grabs the ID from the metadata for special functions (Living Ink, Summoned Servitor)
function getSelfId()
  local metadata = JSON.decode(self.getGMNotes()) or {}
  return metadata.id
end

function isUpgradeActive(row)
  return customizations[row] ~= nil
      and customizations[row].checkboxes ~= nil
      and customizations[row].checkboxes.count ~= nil
      and customizations[row].checkboxes.count > 0
      and selectedUpgrades[row] ~= nil
      and selectedUpgrades[row].xp ~= nil
      and selectedUpgrades[row].xp >= customizations[row].checkboxes.count
end

function resetSelections()
  selectedUpgrades = {}
  updateSave()
  updateDisplay()
end

function createUi()
  if customizations == nil then return end
  for i = 1, #customizations do
    if customizations[i].checkboxes ~= nil then
      createRowCheckboxes(i)
    end
    if customizations[i].textField ~= nil then
      createRowTextField(i)
    end
  end
  self.UI.setXmlTable(xmlTable)
  maybeMakeLivingInkSkillSelectionButtons()
  maybeMakeServitorSlotSelectionButtons()
  updateDisplay()
end

function createRowCheckboxes(rowIndex)
  local checkboxes = customizations[rowIndex].checkboxes

  for col = 1, checkboxes.count do
    -- set up click function
    local funcName = "checkboxRow" .. rowIndex .. "Col" .. col
    local func = function() clickCheckbox(rowIndex, col) end
    self.setVar(funcName, func)

    local cbPos = getCheckboxPosition(rowIndex, col)
    local checkboxXml = {
      tag = "Button",
      attributes = {
        onClick = funcName,
        position = cbPos,
        height = 75,
        width = 75,
        scale = "0.1 0.1 1",
        color = "#00000000"
      }
    }
    table.insert(xmlTable, checkboxXml)

    -- put a text element on top of the invisible buttons for the crosses
    local cbId = "cb_" .. rowIndex .. "_" .. col
    local cbData = getCheckboxData(cbId)
    local labelXml = {
      tag = "Text",
      attributes = {
        id = cbId,
        position = cbPos,
        rotation = "0 0 " .. cbData.angle,
        height = 165,
        width = 165,
        scale = "0.1 0.1 1",
        fontSize = cbData.size,
        text = cbData.symbol,
        textColor = "#000000FF"
      }
    }
    table.insert(xmlTable, labelXml)
  end
end

function getCheckboxPosition(row, col)
  return translatePosition(xInitial + col * xOffset, customizations[row].checkboxes.posZ)
end

-- gets randomized data for a checkbox
function getCheckboxData(cbId)
  -- nil handling
  checkboxData = checkboxData or {}

  -- generate data if not present
  if not checkboxData[cbId] then
    checkboxData[cbId] = {
      angle  = math.random(-12, 12) + 180,
      size   = MathLib.round(math.random(85, 115) / 100 * 125),
      symbol = string.char(CHECKBOX_CHARS[math.random(#CHECKBOX_CHARS)])
    }
  end
  return checkboxData[cbId]
end

function createRowTextField(rowIndex)
  local textField = customizations[rowIndex].textField
  local funcName = "textbox" .. rowIndex
  local func = function(_, value) clickTextbox(rowIndex, value) end
  self.setVar(funcName, func)

  local actualPosition = translatePosition(textField.position[1], textField.position[3])
  local newTextbox = {
    tag = "InputField",
    attributes = {
      onEndEdit = funcName,
      id = rowIndex,
      placeholder = "Click to type",
      position = actualPosition,
      alignment = "MiddleLeft",
      width = textField.width * 1.04,
      height = (inputFontsize + 20),
      fontSize = inputFontsize,
      resizeTextForBestFit = true,
      fontStyle = "Bold",
      rotation = "0 0 180",
      scale = "0.2 0.2 0.2",
      color = "#FFFFFF"
    }
  }
  table.insert(xmlTable, newTextbox)
end

function translatePosition(posX, posZ)
  -- position values are made strings to be usabled by the XML, height (z) is always -22
  local translatedPosX = tostring(posX * -100)
  local translatedPosY = tostring(posZ * 100)
  return translatedPosX .. " " .. translatedPosY .. " -40"
end

function updateDisplay()
  for i = 1, #customizations do
    updateRowDisplay(i)
  end
  maybeUpdateLivingInkSkillDisplay()
  maybeUpdateServitorSlotDisplay()
end

function updateRowDisplay(rowIndex)
  if customizations[rowIndex].checkboxes ~= nil then
    updateCheckboxes(rowIndex)
  end
  if customizations[rowIndex].textField ~= nil then
    updateTextField(rowIndex)
  end
end

function updateCheckboxes(rowIndex)
  local checkboxCount = customizations[rowIndex].checkboxes.count
  local selected = 0
  if selectedUpgrades[rowIndex] ~= nil and selectedUpgrades[rowIndex].xp ~= nil then
    selected = selectedUpgrades[rowIndex].xp
  end

  for col = 1, checkboxCount do
    waitForUILoad("cb_" .. rowIndex .. "_" .. col, "active", col <= selected)
  end
end

function updateTextField(rowIndex)
  if selectedUpgrades[rowIndex] ~= nil and selectedUpgrades[rowIndex].text ~= nil then
    waitForUILoad(rowIndex, "text", selectedUpgrades[rowIndex].text)
  end
end

function waitForUILoad(id, attribute, value)
  if isLoading then
    Wait.condition(
      function()
        Wait.frames(
          function()
            isLoading = false
            self.UI.setAttribute(id, attribute, value)
          end,
          1
        )
      end,
      function() return not self.UI.loading end
    )
  else
    self.UI.setAttribute(id, attribute, value)
  end
end

function clickCheckbox(row, col)
  if selectedUpgrades[row] == nil then
    selectedUpgrades[row] = {}
    selectedUpgrades[row].xp = 0
  end
  if selectedUpgrades[row].xp == col then
    selectedUpgrades[row].xp = col - 1
  else
    selectedUpgrades[row].xp = col
  end
  updateCheckboxes(row)
  updateSave()
  PlayermatApi.syncAllCustomizableCards()
end

-- Updates saved value for given text box when it loses focus
function clickTextbox(rowIndex, value)
  if selectedUpgrades[rowIndex] == nil then
    selectedUpgrades[rowIndex] = {}
  end
  selectedUpgrades[rowIndex].text = value:gsub("^%s*(.-)%s*$", "%1")
  updateSave()
  -- Editing isn't actually done yet, and will block the update. Wait a frame so it's finished
  Wait.frames(function() updateRowDisplay(rowIndex) end, 1)
end

---------------------------------------------------------
-- Living Ink related functions
---------------------------------------------------------

-- Builds the list of boolean skill selections from the Row 1 text field
function maybeLoadLivingInkSkills()
  if selfId ~= "09079-c" then return end
  selectedSkills = {
    willpower = false,
    intellect = false,
    combat    = false,
    agility   = false
  }
  if selectedUpgrades[1] ~= nil and selectedUpgrades[1].text ~= nil then
    for skill in string.gmatch(selectedUpgrades[1].text, "([^,]+)") do
      selectedSkills[skill] = true
    end
  end
end

function clickSkill(skillname)
  selectedSkills[skillname] = not selectedSkills[skillname]
  maybeUpdateLivingInkSkillDisplay()
  updateSelectedLivingInkSkillText()
end

-- Creates the invisible buttons overlaying the skill icons
function maybeMakeLivingInkSkillSelectionButtons()
  if selfId ~= "09079-c" then return end

  local buttonData = {
    function_owner = self,
    position       = { y = 0.2 },
    height         = 130,
    width          = 130,
    color          = { 0, 0, 0, 0 }
  }

  for skillname, _ in pairs(selectedSkills) do
    local funcName = "clickSkill" .. skillname
    self.setVar(funcName, function() clickSkill(skillname) end)

    buttonData.click_function = funcName
    buttonData.position.x = -1 * SKILL_ICON_POSITIONS[skillname].x
    buttonData.position.z = SKILL_ICON_POSITIONS[skillname].z
    self.createButton(buttonData)
  end
end

-- Builds a comma-delimited string of skills and places it in the Row 1 text field
function updateSelectedLivingInkSkillText()
  local skillString = ""
  if selectedSkills.willpower then
    skillString = skillString .. "willpower" .. ","
  end
  if selectedSkills.intellect then
    skillString = skillString .. "intellect" .. ","
  end
  if selectedSkills.combat then
    skillString = skillString .. "combat" .. ","
  end
  if selectedSkills.agility then
    skillString = skillString .. "agility" .. ","
  end
  if selectedUpgrades[1] == nil then
    selectedUpgrades[1] = {}
  end
  selectedUpgrades[1].text = skillString
  updateSave()
end

-- Refresh the vector circles indicating a skill is selected. Since we can only have one table of
-- vectors set, have to refresh all 4 at once
function maybeUpdateLivingInkSkillDisplay()
  if selfId ~= "09079-c" then return end
  local circles = {}
  for skill, isSelected in pairs(selectedSkills) do
    if isSelected then
      local circle = getCircleVector(SKILL_ICON_POSITIONS[skill])
      if circle ~= nil then
        table.insert(circles, circle)
      end
    end
  end
  self.setVectorLines(circles)
end

function getCircleVector(center)
  local diameter = Vector(0, 0, 0.1)
  local pointOfOrigin = Vector(center.x, Y_VISIBLE, center.z)
  local vec
  local vecList = {}
  local arcStep = 5
  for i = 0, 360, arcStep do
    diameter:rotateOver('y', arcStep)
    vec = pointOfOrigin + diameter
    vec.y = pointOfOrigin.y
    table.insert(vecList, vec)
  end

  return {
    points    = vecList,
    color     = VECTOR_COLOR.mystic,
    thickness = 0.02
  }
end

---------------------------------------------------------
-- Summoned Servitor related functions
---------------------------------------------------------

-- Creates the invisible buttons overlaying the slot words
function maybeMakeServitorSlotSelectionButtons()
  if selfId ~= "09080-c" then return end

  local buttonData = {
    click_function = "clickArcane",
    function_owner = self,
    position       = { x = -1 * SLOT_ICON_POSITIONS.arcane.x, y = 0.2, z = SLOT_ICON_POSITIONS.arcane.z },
    height         = 130,
    width          = SLOT_ICON_POSITIONS["arcane"].width * 1000 + 5,
    color          = { 0, 0, 0, 0 }
  }
  self.createButton(buttonData)

  buttonData.click_function = "clickAlly"
  buttonData.position.x = -1 * SLOT_ICON_POSITIONS.ally.x
  buttonData.width = SLOT_ICON_POSITIONS["ally"].width * 1000 + 5
  self.createButton(buttonData)
end

-- toggles the clicked slot
function clickArcane()
  if selectedUpgrades[6] == nil then
    selectedUpgrades[6] = {}
  end
  if selectedUpgrades[6].text == SUMMONED_SERVITOR_SLOT_INDICES.arcane then
    selectedUpgrades[6].text = SUMMONED_SERVITOR_SLOT_INDICES.none
  else
    selectedUpgrades[6].text = SUMMONED_SERVITOR_SLOT_INDICES.arcane
  end
  updateSave()
  maybeUpdateServitorSlotDisplay()
end

-- toggles the clicked slot
function clickAlly()
  if selectedUpgrades[6] == nil then
    selectedUpgrades[6] = {}
  end
  if selectedUpgrades[6].text == SUMMONED_SERVITOR_SLOT_INDICES.ally then
    selectedUpgrades[6].text = SUMMONED_SERVITOR_SLOT_INDICES.none
  else
    selectedUpgrades[6].text = SUMMONED_SERVITOR_SLOT_INDICES.ally
  end
  updateSave()
  maybeUpdateServitorSlotDisplay()
end

-- Refresh the vector circles indicating a slot is selected.
function maybeUpdateServitorSlotDisplay()
  if selfId ~= "09080-c" then return end

  local center         = SLOT_ICON_POSITIONS["arcane"]
  local arcaneVecList  = {
    Vector(center.x + center.width, Y_VISIBLE, center.z + 0.05),
    Vector(center.x - center.width, Y_VISIBLE, center.z + 0.05),
    Vector(center.x - center.width, Y_VISIBLE, center.z - 0.05),
    Vector(center.x + center.width, Y_VISIBLE, center.z - 0.05),
    Vector(center.x + center.width, Y_VISIBLE, center.z + 0.05)
  }

  center               = SLOT_ICON_POSITIONS["ally"]
  local allyVecList    = {
    Vector(center.x + center.width, Y_VISIBLE, center.z + 0.05),
    Vector(center.x - center.width, Y_VISIBLE, center.z + 0.05),
    Vector(center.x - center.width, Y_VISIBLE, center.z - 0.05),
    Vector(center.x + center.width, Y_VISIBLE, center.z - 0.05),
    Vector(center.x + center.width, Y_VISIBLE, center.z + 0.05)
  }

  local arcaneVecColor = VECTOR_COLOR.unselected
  local allyVecColor   = VECTOR_COLOR.unselected

  if selectedUpgrades[6] ~= nil and selectedUpgrades[6].text == SUMMONED_SERVITOR_SLOT_INDICES.arcane then
    arcaneVecColor = VECTOR_COLOR.mystic
  elseif selectedUpgrades[6] ~= nil and selectedUpgrades[6].text == SUMMONED_SERVITOR_SLOT_INDICES.ally then
    allyVecColor = VECTOR_COLOR.mystic
  end

  self.setVectorLines({
    {
      points    = arcaneVecList,
      color     = arcaneVecColor,
      thickness = 0.02
    },
    {
      points    = allyVecList,
      color     = allyVecColor,
      thickness = 0.02
    }
  })
end
end)
__bundle_register("playermat/PlayermatApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local PlayermatApi              = {}
  local GUIDReferenceApi          = require("core/GUIDReferenceApi")
  local SearchLib                 = require("util/SearchLib")
  local localInvestigatorPosition = Vector(-1.17, 1, -0.01)

  -- General notes:
  -------------------------------------------------------------------
  -- "matColor" is a string that describes the internal "color" of each mat
  -- (the starting color when the game is first loaded)
  -- Some functions will support the additional "All" pseudo-color to trigger that code for each mat
  -- If a function does not support "All", there will be a comment
  -------------------------------------------------------------------
  -- "playerColor" (or "handColor") is a string that describes the actual color of the seat
  -------------------------------------------------------------------

  -- Convenience function to look up a mat's object by color, or get all mats
  local function getMatForColor(matColor)
    if matColor == "All" then
      return GUIDReferenceApi.getObjectsByType("Playermat") or {}
    else
      return { matColor = GUIDReferenceApi.getObjectByOwnerAndType(matColor, "Playermat") }
    end
  end

  -- Convenience function to call a function on a single mat
  ---@param matColor string Does not support "All"
  ---@param funcName string Name of the function to call
  ---@param params any Parameter for the call
  local function callForSingleMat(matColor, funcName, params)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call(funcName, params)
    end
  end

  -- Returns the color of the closest playermat
  ---@param startPos table Starting position to get the closest mat from
  function PlayermatApi.getMatColorByPosition(startPos)
    local result, smallestDistance
    for matColor, mat in pairs(getMatForColor("All")) do
      local distance = Vector.between(startPos, mat.getPosition()):magnitude()
      if smallestDistance == nil or distance < smallestDistance then
        smallestDistance = distance
        result = matColor
      end
    end
    return result
  end

  -- Returns the color of the player's hand that is seated next to the playermat
  ---@param matColor string Does not support "All"
  function PlayermatApi.getPlayerColor(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getVar("playerColor")
    end
  end

  -- Returns the color of the playermat that owns the playercolor's hand
  ---@param handColor string Color of the playermat
  function PlayermatApi.getMatColor(handColor)
    for matColor, mat in pairs(getMatForColor("All")) do
      if mat.getVar("playerColor") == handColor then
        return matColor
      end
    end
  end

  -- Gets the slot data for the playermat
  ---@param matColor string Does not support "All"
  function PlayermatApi.getSlotData(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getTable("slotData")
    end
  end

  -- Sets the slot data for the playermat
  ---@param matColor string Does not support "All"
  ---@param newSlotData table New slot data for the playermat
  function PlayermatApi.loadSlotData(matColor, newSlotData)
    return callForSingleMat(matColor, "updateSlotSymbols", newSlotData)
  end

  -- Performs a search of the deck area of the requested playermat and returns the result as table
  ---@param matColor string Does not support "All"
  function PlayermatApi.getDeckAreaObjects(matColor)
    return callForSingleMat(matColor, "getDeckAreaObjects")
  end

  -- Flips the top card of the deck (useful after deck manipulation for Norman Withers)
  ---@param matColor string Does not support "All"
  function PlayermatApi.flipTopCardFromDeck(matColor)
    return callForSingleMat(matColor, "flipTopCardFromDeck")
  end

  -- Returns the position of the discard pile of the requested playermat
  ---@param matColor string Does not support "All"
  function PlayermatApi.getDiscardPosition(matColor)
    return Vector(callForSingleMat(matColor, "returnGlobalDiscardPosition"))
  end

  -- Returns the position of the draw pile of the requested playermat
  ---@param matColor string Does not support "All"
  function PlayermatApi.getDrawPosition(matColor)
    return Vector(callForSingleMat(matColor, "returnGlobalDrawPosition"))
  end

  -- Transforms a local position into a global position
  ---@param localPos table Local position to be transformed
  ---@param matColor string Does not support "All"
  function PlayermatApi.transformLocalPosition(localPos, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.positionToWorld(localPos)
    end
  end

  -- Returns the rotation of the requested playermat
  ---@param matColor string Does not support "All"
  function PlayermatApi.returnRotation(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getRotation()
    end
  end

  -- Returns a table with spawn data (position and rotation) for a helper object
  ---@param helperName string Name of the helper object
  function PlayermatApi.getHelperSpawnData(matColor, helperName)
    local resultTable = {}
    for color, mat in pairs(getMatForColor(matColor)) do
      local data = mat.call("getHelperSpawnData", helperName)
      resultTable[color] = { position = Vector(data.position), rotation = Vector(data.rotation) }
    end
    return resultTable
  end

  -- Triggers the Upkeep for the requested playermat
  ---@param playerColor string Color of the calling player (for messages)
  function PlayermatApi.doUpkeepFromHotkey(matColor, playerColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("doUpkeepFromHotkey", playerColor)
    end
  end

  -- Handles discarding for the requested playermat for the provided list of objects
  ---@param matColor string Does not support "All"
  ---@param objList table List of objects to discard
  function PlayermatApi.discardListOfObjects(matColor, objList)
    return callForSingleMat(matColor, "discardListOfObjects", objList)
  end

  -- Gets data about the active investigator
  ---@param matColor string Does not support "All"
  function PlayermatApi.getActiveInvestigatorData(matColor)
    return callForSingleMat(matColor, "getActiveInvestigatorData")
  end

  -- Sets data about the active investigator
  ---@param newData table New active investigator data (class and id)
  function PlayermatApi.setActiveInvestigatorData(matColor, newData)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("setActiveInvestigatorData", newData)
    end
  end

  -- Returns the position for encounter card drawing
  ---@param matColor string Does not support "All"
  ---@param stack boolean If true, returns the leftmost position instead of the first empty from the right
  function PlayermatApi.getEncounterCardDrawPosition(matColor, stack)
    return Vector(callForSingleMat(matColor, "getEncounterCardDrawPosition", stack))
  end

  -- Sets the requested playermat's snap points to limit snapping to matching card types or not
  ---@param matchCardTypes boolean Whether snap points should only snap for the matching card types
  function PlayermatApi.setLimitSnapsByType(matchCardTypes, matColor)
    return callForSingleMat(matColor, "setLimitSnapsByType", matchCardTypes)
  end

  -- Sets the requested playermat's draw 1 button to visible
  ---@param isDrawButtonVisible boolean Whether the draw 1 button should be visible or not
  function PlayermatApi.showDrawButton(isDrawButtonVisible, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("showDrawButton", isDrawButtonVisible)
    end
  end

  -- Updates clue counts to account for clickable clue counters
  ---@param showCounter boolean Whether the clickable counter should be present or not
  function PlayermatApi.clickableClues(showCounter, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("clickableClues", showCounter)
    end
  end

  -- Toggles the use of class textures for the requested playermat
  ---@param state boolean Whether the class texture should be used or not
  function PlayermatApi.useClassTexture(state, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("useClassTexture", state)
    end
  end

  -- updates the texture of the playermat
  ---@param overrideName? string Force a specific texture
  function PlayermatApi.updateTexture(matColor, overrideName)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("updateTexture", overrideName)
    end
  end

  -- Removes all clues (to the trash for tokens and counters set to 0) for the requested playermat
  function PlayermatApi.removeClues(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("removeClues")
    end
  end

  -- Reports the clue count for the requested playermat
  function PlayermatApi.getClueCount(matColor)
    local count = 0
    for _, mat in pairs(getMatForColor(matColor)) do
      count = count + (mat.call("getClueCount") or 0)
    end
    return count
  end

  -- Reports the doom count for the requested playermat
  function PlayermatApi.getDoomCount(matColor)
    local count = 0
    for _, mat in pairs(getMatForColor(matColor)) do
      count = count + (mat.call("getDoomCount") or 0)
    end
    return count
  end

  -- Updates the specified owned counter
  ---@param type string Counter to target
  ---@param newValue number Value to set the counter to
  ---@param modifier number If newValue is not provided, the existing value will be adjusted by this modifier
  function PlayermatApi.updateCounter(matColor, type, newValue, modifier)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("updateCounter", { type = type, newValue = newValue, modifier = modifier })
    end
  end

  -- Triggers the draw function for the specified playermat
  ---@param number number Amount of cards to draw
  function PlayermatApi.drawCardsWithReshuffle(matColor, number)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("drawCardsWithReshuffle", number)
    end
  end

  -- Returns the resource counter amount
  ---@param matColor string Does not support "All"
  ---@param type string Counter to target
  function PlayermatApi.getCounterValue(matColor, type)
    return callForSingleMat(matColor, "getCounterValue", type)
  end

  -- Returns a list of mat colors that have an investigator placed
  function PlayermatApi.getUsedMatColors()
    local usedColors = {}
    for matColor, mat in pairs(getMatForColor("All")) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = SearchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult > 0 then
        table.insert(usedColors, matColor)
      end
    end
    return usedColors
  end

  -- Returns a list of investigator card objects
  function PlayermatApi.getUsedInvestigatorCards()
    local usedCards = {}
    for matColor, mat in pairs(getMatForColor("All")) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = SearchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult > 0 then
        usedCards[matColor] = searchResult[1]
      end
    end
    return usedCards
  end

  -- Returns investigator name
  ---@param matColor string Does not support "All"
  function PlayermatApi.getInvestigatorName(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = SearchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult == 1 then
        return searchResult[1].getName()
      end
    end
    return ""
  end

  -- Resets the specified skill tracker to "1, 1, 1, 1"
  function PlayermatApi.resetSkillTracker(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("resetSkillTracker")
    end
  end

  -- Finds all objects on the playermat and associated set aside zone and returns a table
  ---@param filter? string Name of the filte function (see util/SearchLib)
  function PlayermatApi.searchAroundPlayermat(matColor, filter)
    local objList = {}
    for _, mat in pairs(getMatForColor(matColor)) do
      for _, obj in ipairs(mat.call("searchAroundSelf", filter)) do
        table.insert(objList, obj)
      end
    end
    return objList
  end

  -- Spawns the regular action tokens
  function PlayermatApi.spawnActionTokens(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("spawnActionTokens")
    end
  end

  -- Triggers the metadata sync for all playermats
  function PlayermatApi.syncAllCustomizableCards()
    for _, mat in pairs(getMatForColor("All")) do
      mat.call("syncAllCustomizableCards")
    end
  end

  -- Gets the value of the "Use Resource Counters" option that's set in the mat's option panel
  ---@param matColor string Does not support "All"
  function PlayermatApi.getResourceCounterOption(matColor)
    return callForSingleMat(matColor, "getResourceCounterOption")
  end

  -- Gets the value of the "Show Token Splash" option that's set in the mat's option panel
  ---@param matColor string Does not support "All"
  function PlayermatApi.getTokenSplashOption(matColor)
    return callForSingleMat(matColor, "getTokenSplashOption")
  end

  -- Gets the exhaust rotation that's set in the mat's option panel
  ---@param matColor string Does not support "All"
  ---@param convertToGlobal? boolean True if the global (Vector) rotation is requested (otherwise just local Y-rotation)
  function PlayermatApi.getExhaustRotation(matColor, convertToGlobal)
    return callForSingleMat(matColor, "getExhaustRotation", convertToGlobal)
  end

  -- moves + rotates a playermat (and related objects)
  ---@param position? table New position for the playermat
  ---@param rotationY? number New y-rotation for the playermat (X and Z will be 0)
  ---@param positionOffset? table Positional offset for the playermat
  function PlayermatApi.moveAndRotate(matColor, position, rotationY, positionOffset)
    local params = { position = position, rotationY = rotationY, positionOffset = positionOffset }
    return callForSingleMat(matColor, "moveAndRotateSelf", params)
  end

  -- Instructs the playermat to not touch the regular action tokens for the next investigator change
  function PlayermatApi.activateTransformEffect(matColor)
    return callForSingleMat(matColor, "activateTransformEffect")
  end

  return PlayermatApi
end
end)
__bundle_register("util/MathLib", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local MathLib = {}

  -- Rounds a number to a given number of decimal places
  ---@param num number The number to round
  ---@param numDecimalPlaces? number The number of decimal places to round to (defaults to 0)
  ---@return number: The rounded number
  function MathLib.round(num, numDecimalPlaces)
    local mult = 10 ^ (numDecimalPlaces or 0)
    return math.floor(num * mult + 0.5) / mult
  end

  -- Rounds a number to the nearest multiple of a given base
  ---@param n number The number to round
  ---@param base number The base to round to the nearest multiple of
  ---@return number: The number rounded to the nearest multiple of the base
  function MathLib.roundToMultiple(n, base)
    return math.floor(n / base + 0.5) * base
  end

  -- Rounds an angle to the nearest multiple and keeps it within the 0-360 degree range
  ---@param angle number The angle in degrees
  ---@param base number The base multiple to round the angle to
  ---@return number: The rounded angle, wrapped to the range [0, 360)
  function MathLib.roundAngleToMultiple(angle, base)
    return MathLib.roundToMultiple(angle, base) % 360
  end

  -- Rounds a number to a given number of decimal places
  ---@param vec tts__Vector The vector to round
  ---@param numDecimalPlaces? number The number of decimal places to round to (defaults to 0)
  ---@return tts__Vector: The rounded vector
  function MathLib.roundVector(vec, numDecimalPlaces)
    return Vector(
      MathLib.round(vec.x, numDecimalPlaces),
      MathLib.round(vec.y, numDecimalPlaces),
      MathLib.round(vec.z, numDecimalPlaces)
    )
  end

  -- Clamps a value between a minimum and maximum value
  ---@param val number The input value
  ---@param min number The minimum value
  ---@param max number The maximum value
  ---@return number: The clamped value
  function MathLib.clamp(val, min, max)
    return math.max(min, math.min(max, val))
  end

  -- Linearly interpolates between two points
  ---@param a number The start value
  ---@param b number The end value
  ---@param t number The interpolation factor (typically between 0 and 1)
  ---@return number: The interpolated value
  function MathLib.lerp(a, b, t)
    return a + (b - a) * t
  end

  return MathLib
end
end)
__bundle_register("util/SearchLib", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local SearchLib = {}
  local FILTER_FUNCTIONS = {
    isCard           = function(x) return x.type == "Card" end,
    isDeck           = function(x) return x.type == "Deck" end,
    isCardOrDeck     = function(x) return x.type == "Card" or x.type == "Deck" end,
    isClue           = function(x) return x.memo == "clueDoom" and x.is_face_down == false end,
    isDoom           = function(x) return x.memo == "clueDoom" and x.is_face_down == true end,
    isInteractable   = function(x) return x.interactable end,
    isTileOrToken    = function(x) return not x.Book and (x.type == "Tile" or x.type == "Generic") end,
    isUniversalToken = function(x) return x.getMemo() == "universalActionAbility" end,
  }

  -- performs the actual search and returns a filtered list of object references
  ---@param pos tts__Vector Global position
  ---@param rot? tts__Vector Global rotation
  ---@param size table Size
  ---@param filter? string Name of the filter function
  ---@param direction? table Direction (positive is up)
  ---@param maxDistance? number Distance for the cast
  ---@param debug? boolean Whether the debug boxes should be shown
  local function returnSearchResult(pos, rot, size, filter, direction, maxDistance, debug)
    local filterFunc = filter and FILTER_FUNCTIONS[filter]
    local searchResult = Physics.cast({
      origin       = pos,
      direction    = direction or { 0, 1, 0 },
      orientation  = rot or { 0, 0, 0 },
      type         = 3,
      size         = size,
      max_distance = maxDistance or 0,
      debug        = debug or false
    })

    -- filter the result for matching objects
    local objList = {}
    for _, v in ipairs(searchResult) do
      if (not filter or filterFunc(v.hit_object)) then
        table.insert(objList, v.hit_object)
      end
    end
    return objList
  end

  -- searches the specified area
  function SearchLib.inArea(pos, rot, size, filter, debug)
    return returnSearchResult(pos, rot, size, filter, nil, nil, debug)
  end

  -- searches the area on an object
  function SearchLib.onObject(obj, filter, scale, debug)
    scale      = scale or 1
    local pos  = obj.getPosition() + Vector(0, 1, 0) -- offset by half the cast's height
    local size = obj.getBounds().size:scale(scale):setAt("y", 2)
    return returnSearchResult(pos, nil, size, filter, nil, nil, debug)
  end

  -- searches the area directly below an object
  function SearchLib.belowObject(obj, filter, scale, debug)
    scale        = scale or 1
    local objPos = obj.getPosition()
    local pos    = objPos + Vector(0, -objPos.y / 2, 0) -- offset by half the cast's height
    local size   = obj.getBounds().size:scale(scale):setAt("y", objPos.y)
    return returnSearchResult(pos, nil, size, filter, nil, nil, debug)
  end

  -- searches the specified position (a single point)
  function SearchLib.atPosition(pos, filter, debug)
    local size = { 0.1, 2, 0.1 }
    return returnSearchResult(pos, nil, size, filter, nil, nil, debug)
  end

  -- searches below the specified position (downwards until y = 0)
  function SearchLib.belowPosition(pos, filter, debug)
    local size = { 0.1, 2, 0.1 }
    local direction = { 0, -1, 0 }
    local maxDistance = pos.y
    return returnSearchResult(pos, nil, size, filter, direction, maxDistance, debug)
  end

  return SearchLib
end
end)
return __bundle_require("__root")
`;
}
