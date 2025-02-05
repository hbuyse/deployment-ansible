return {
  {
    -- Indentation guides to all lines (including empty lines)
    'lukas-reineke/indent-blankline.nvim',
    main = 'ibl',
    init = function()
      local hooks = require('ibl.hooks')
      hooks.register(hooks.type.SCOPE_HIGHLIGHT, hooks.builtin.scope_highlight_from_extmark)
    end,
    opts = {
      scope = {
        enabled = true,
        show_start = false,
        show_end = false,
        include = {
          node_type = { ['*'] = { '*' } },
        },
        highlight = 'Debug',
      },
      indent = {
        char = { '|', '¦', '┆', '┊' },
      },
      exclude = {
        buftypes = {
          'nofile',
          'prompt',
          'quickfix',
          'terminal',
        },
        filetypes = {
          'startify',
          'dashboard',
          'dotooagenda',
          'log',
          'fugitive',
          'gitcommit',
          'packer',
          'vimwiki',
          'markdown',
          'json',
          'txt',
          'vista',
          'help',
          'todoist',
          'NvimTree',
          'peekaboo',
          'git',
          'TelescopePrompt',
          'undotree',
          'flutterToolsOutline',
          '', -- for all buffers without a file type
        },
      },
    },
  },
}
