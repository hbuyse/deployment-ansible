local rule = {
  matches = {
    {
      { 'device.nick', 'equals', 'WD19 Dock' },
    },
  },
  apply_properties = {
    ['device.disabled'] = true,
  },
}

table.insert(alsa_monitor.rules, rule)
