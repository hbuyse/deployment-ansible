return {
  'GR3YH4TT3R93/zellij-nav.nvim',

  -- Only load plugin if in active Zellij instance
  cond = os.getenv('ZELLIJ') ~= nil,

  -- Lazy load plugin for improved startup times
  lazy = true,
  event = 'VeryLazy',
  -- init = function() -- Only needed if you want to override default keymaps otherwise just call opts = {}
  --   vim.g.zellij_nav_default_mappings = false -- Default: true
  -- end,
  opts = {},
  keys = {
    { '<C-h>', '<cmd>ZellijNavigateLeft<CR>', { silent = true, desc = 'Move to Zellij pane left' } },
    { '<C-j>', '<cmd>ZellijNavigateDown<CR>', { silent = true, desc = 'Move to Zellij pane down' } },
    { '<C-k>', '<cmd>ZellijNavigateUp<CR>', { silent = true, desc = 'Move to Zellij pane up' } },
    { '<C-l>', '<cmd>ZellijNavigateRight<CR>', { silent = true, desc = 'Move to Zellij pane right' } },
    { '<M-c>', '<cmd>ZellijNewPaneVSplit<CR>', { silent = true, desc = 'Open new vertical Zellij pane' } },
  },
}
