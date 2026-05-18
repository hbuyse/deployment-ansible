--- Disable some audio devices.
-- @module 89-disable-devices

local rules = {
  {
    matches = {
      {
        { "device.nick", "equals", "WD19 Dock" },
      },
    },
    apply_properties = {
      ["device.disabled"] = true,
    },
  },
  {
    matches = {
      {
        { "device.nick", "equals", "sof-soundwire" },
      },
    },
    apply_properties = {
      ["device.disabled"] = true,
    },
  },
}

for _, rule in ipairs(rules) do
  table.insert(alsa_monitor.rules, rule)
end
