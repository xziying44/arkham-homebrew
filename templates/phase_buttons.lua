-- Bundled by luabundle {"version":"1.6.0"}
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
					local identifier = type(name) == 'string' and '"' .. name .. '"' or tostring(name)
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
require("playercards/CardsWithPhaseButtons")
end)
__bundle_register("playercards/CardsWithHelper", function(require, _LOADED, __bundle_register, __bundle_modules)
--[[ Library for cards that have helpers
This file is used to share code between cards with helpers.
It syncs the visibility of the helper with the option panel and
makes sure the card has the respective tag.
Additionally, it will call 'initialize()' and 'shutOff()'
in the parent file if they are present.

Instructions:
1) Define the global variables before requiring this file:
hasXML          = true  (whether the card has an XML display)
isHelperEnabled = false (default state of the helper, should be 'false')

2) Add "CardWithHelper" tag to .json for the card object itself.

3) Add `if isHelperEnabled then updateDisplay() end` to onLoad()

----------------------------------------------------------]]

-- forces a new state
function setHelperState(newState)
  if doNotTurnOff == true then return end
  isHelperEnabled = newState
  updateSave()
  updateDisplay()
end

-- toggles the current state
function toggleHelper(manual)
  if manual and isHelperEnabled == true then -- do not allow helper to be forced to turn on
    doNotTurnOff = true
  elseif manual and isHelperEnabled == false then -- return to default behavior
    doNotTurnOff = false
  end
  isHelperEnabled = not isHelperEnabled
  updateSave()
  updateDisplay()
end

-- updates the visibility and calls events (after a small delay to allow XML being set)
function updateDisplay()
  Wait.frames(actualDisplayUpdate, 5)
end

function actualDisplayUpdate()
  if isHelperEnabled then
    self.clearContextMenu()
    self.addContextMenuItem("Disable Helper", toggleHelper)
    if hasXML then self.UI.show("Helper") end
    if initialize then initialize() end
  else
    self.clearContextMenu()
    self.addContextMenuItem("Enable Helper", toggleHelper)
    if hasXML then self.UI.hide("Helper") end
    if shutOff then shutOff() end
  end
  if generateContextMenu then generateContextMenu() end
end

function onPickUp()
  setHelperState(false)
end
end)
__bundle_register("playercards/CardsWithPhaseButtons", function(require, _LOADED, __bundle_register, __bundle_modules)
require("playercards/CardsWithHelper")
local SideButtonCreator = require("util/SideButtonCreator")

-- intentionally global
hasXML                  = true
isHelperEnabled         = false

-- BUTTON_PARAMS_PLACEHOLDER --

local buttonIdToIndex   = {
  <!-- BUTTON_ID_INDEX_PLACEHOLDER -->
}

---------------------------------------------------------
-- general setup
---------------------------------------------------------

function updateSave()
  self.script_state = JSON.encode({ isHelperEnabled = isHelperEnabled })
end

function onLoad(savedData)
  self.addTag("CardWithHelper")
  self.addTag("DoInUpkeep")

  if savedData and savedData ~= "" then
    local loadedData = JSON.decode(savedData)
    isHelperEnabled = loadedData.isHelperEnabled
  end

  createHelperXML()

  if isHelperEnabled then
    updateDisplay()
  end
end

function createHelperXML()
  local xmlTable = SideButtonCreator.getXmlTable(buttonParams)
  self.UI.setXmlTable(xmlTable)
end

---------------------------------------------------------
-- main functionality
---------------------------------------------------------

-- sets the state for all buttons
function setUiState(params)
  for buttonId, state in pairs(params) do
    setStateForButton(state, buttonId)
  end
end

-- sets the state for a specific button
function setStateForButton(state, buttonId)
  -- if state is omitted, get it from the XML and toggle it
  if not state then
    state = (self.UI.getAttribute(buttonId, "buttonState") == "off")
  end

  local color = buttonParams.buttonColors[buttonIdToIndex[buttonId]]
  self.UI.setAttribute(buttonId, "color", state and color or "#353535E6")
  self.UI.setAttribute(buttonId, "textColor", state and "white" or "#A0A0A0")
  self.UI.setAttribute(buttonId, "buttonState", state and "on" or "off")
end

-- toggles the state for the clicked button
function onClick_sideButton(_, _, buttonId)
  setStateForButton(nil, buttonId)
end

-- called by the Upkeep function - sets all buttons to enabled
function doInUpkeep()
  for _, buttonId in ipairs(buttonParams.buttonIds) do
    setStateForButton(true, buttonId)
  end
end
end)
__bundle_register("util/SideButtonCreator", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local SideButtonCreator = {}

  -- generates the XML table for the defaults
  local function generateDefaults(buttonCount)
    local defaults = {
      tag = "Defaults",
      children = {
        {
          tag = "Button",
          attributes = {
            font          = "font_arkhamicons",
            fontSize      = "300",
            textAlignment = "UpperCenter", -- results in almost vertically centered reaction symbols
            onClick       = "onClick_sideButton"
          }
        },
        {
          tag = "TableLayout",
          attributes = {
            position            = "0 188 -40",
            rotation            = "0 0 90",
            height              = buttonCount * 400,
            width               = "700",
            scale               = "0.1 0.1 1",
            cellSpacing         = "70",
            cellPadding         = "0 6 6 6",
            cellBackgroundColor = "rgba(1,1,1,0)",
            rowBackgroundColor  = "rgba(0,0,0,0.666)"
          }
        }
      }
    }
    return defaults
  end

  -- main function - creates and returns the XML table for the side buttons
  function SideButtonCreator.getXmlTable(params)
    -- defaults for parameters
    params              = params or {}
    params.buttonCount  = params.buttonCount or <!-- BUTTON_COUNT -->
    params.buttonLabels = params.buttonLabels or {}
    params.buttonIds    = params.buttonIds or {}
    params.buttonColors = params.buttonColors or {}

    -- create the XML table
    local xmlTable      = {}

    -- get the defaults
    table.insert(xmlTable, generateDefaults(params.buttonCount))

    -- create the table layout
    local tableLayoutXml = {
      tag = "TableLayout",
      attributes = { id = "Helper", active = "false" },
      children = {}
    }

    -- add the buttons to it
    for i = 1, params.buttonCount do
      local buttonXml = {
        tag = "Row",
        attributes = { id = "Row" .. i },
        children = {
          {
            tag = "Cell",
            children = {
              {
                tag = "Button",
                attributes = {
                  buttonState = "on",
                  id          = params.buttonIds[i] or ("Button" .. i),
                  color       = params.buttonColors[i] or "white",
                  text        = params.buttonLabels[i] or ""
                }
              }
            }
          }
        }
      }

      table.insert(tableLayoutXml.children, buttonXml)
    end

    -- add to the XmlTable
    table.insert(xmlTable, tableLayoutXml)

    return xmlTable
  end

  return SideButtonCreator
end
end)
return __bundle_require("__root")

