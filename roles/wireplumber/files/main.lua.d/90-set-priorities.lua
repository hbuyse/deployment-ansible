-- Jabra is always prioritized
local properties = {
  ['Jabra SPEAK 510 USB'] = { playback = 1500, capture = 2500 },
  ['HyperX Cloud II Wireless'] = { playback = 1499, capture = 2499 },
  ['HyperX Virtual Surround Sound'] = { playback = 1499, capture = 2499 },
}

for name, priorities in pairs(properties) do
  for stream, priority in pairs(priorities) do
    local rule = {
      matches = {
        {
          { 'node.nick', 'equals', name },
          { 'api.alsa.pcm.stream', 'equals', stream },
        },
      },
      apply_properties = {
        ['priority.driver'] = priority,
        ['priority.session'] = priority,
      },
    }

    table.insert(alsa_monitor.rules, rule)
  end
end
